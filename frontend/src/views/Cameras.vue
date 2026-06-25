<template>
  <div>
    <div class="page-title">设备管理</div>
    <div class="page-desc">登记现场摄像头档案（RTSP/IP/USB），一键启停拉流检测，状态一目了然。</div>

    <el-card shadow="never">
      <div class="bar">
        <el-button type="primary" :icon="Plus" @click="openCreate">新增摄像头</el-button>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
        <span class="hint">提示：海康主码流 <code>rtsp://用户名:密码@IP:554/Streaming/Channels/101</code>，子码流 102</span>
      </div>

      <el-table :data="cams" v-loading="loading" style="margin-top: 12px">
        <el-table-column label="名称" prop="name" min-width="140" />
        <el-table-column label="安装位置" min-width="140">
          <template #default="{ row }">{{ row.location || '—' }}</template>
        </el-table-column>
        <el-table-column label="地址" min-width="280">
          <template #default="{ row }">
            <code class="url">{{ row.url }}</code>
          </template>
        </el-table-column>
        <el-table-column label="健康状态" width="160">
          <template #default="{ row }">
            <el-tag v-if="row.healthState === 'online'" type="success" size="small">
              <span class="dot online" /> 在线
            </el-tag>
            <el-tag v-else-if="row.healthState === 'error'" type="danger" size="small">
              <span class="dot error" /> 异常
            </el-tag>
            <el-tag v-else-if="row.healthState === 'recent'" type="warning" size="small">
              <span class="dot recent" /> 心跳停止 {{ formatGap(row.offlineFor) }}
            </el-tag>
            <el-tag v-else-if="row.healthState === 'offline'" type="danger" effect="dark" size="small">
              <span class="dot offline" /> 离线 {{ formatGap(row.offlineFor) }}
            </el-tag>
            <el-tag v-else type="info" size="small">从未启动</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.online"
              link
              type="success"
              :disabled="!row.enabled"
              @click="start(row)"
            >开启</el-button>
            <el-button v-else link type="warning" @click="stop(row)">停止</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑 -->
    <el-dialog v-model="dialogVisible" :title="editing ? '编辑摄像头' : '新增摄像头'" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="如：1号塔吊监控" />
        </el-form-item>
        <el-form-item label="安装位置">
          <el-input v-model="form.location" placeholder="选填，如：工地东南角" />
        </el-form-item>
        <el-form-item label="RTSP 地址">
          <el-input
            v-model="form.url"
            type="textarea"
            :rows="2"
            placeholder="rtsp://用户名:密码@IP:554/Streaming/Channels/101"
          />
        </el-form-item>
        <el-form-item label="置信度">
          <el-slider v-model="form.conf" :min="0.1" :max="0.9" :step="0.05" style="width: 220px" :format-tooltip="(v) => v.toFixed(2)" />
          <span class="conf-val">{{ form.conf.toFixed(2) }}</span>
        </el-form-item>
        <el-form-item label="抓拍间隔">
          <el-select v-model="form.snapInterval" style="width: 140px">
            <el-option label="5 秒" :value="5" />
            <el-option label="10 秒" :value="10" />
            <el-option label="30 秒" :value="30" />
            <el-option label="60 秒" :value="60" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-divider style="margin: 8px 0" />
        <el-form-item label="开启时段">
          <el-switch v-model="form.scheduleEnabled" />
          <span class="tip">仅在该时段内做 AI 识别，外则只拉流不检测，省 CPU 减少夜班误报</span>
        </el-form-item>
        <el-form-item v-if="form.scheduleEnabled" label="作业时间">
          <el-time-picker
            v-model="form.scheduleStart"
            placeholder="开始"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 130px"
          />
          <span style="margin: 0 8px">至</span>
          <el-time-picker
            v-model="form.scheduleEnd"
            placeholder="结束"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 130px"
          />
          <span class="tip">支持跨夜（如 22:00 至 06:00）</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import {
  fetchCameras, createCamera, updateCamera, deleteCamera,
  startCamera, stopCamera,
} from '@/api/cameras'

const cams = ref([])
const loading = ref(false)
const saving = ref(false)

const dialogVisible = ref(false)
const editing = ref(false)
const form = reactive({
  id: null, name: '', location: '', url: '',
  conf: 0.5, snapInterval: 10, enabled: true,
  scheduleEnabled: false, scheduleStart: '07:00', scheduleEnd: '19:00',
})

let pollTimer = null

const load = async () => {
  loading.value = true
  try {
    const res = await fetchCameras()
    cams.value = res.items
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editing.value = false
  Object.assign(form, {
    id: null, name: '', location: '', url: '',
    conf: 0.5, snapInterval: 10, enabled: true,
    scheduleEnabled: false, scheduleStart: '07:00', scheduleEnd: '19:00',
  })
  dialogVisible.value = true
}
const openEdit = (row) => {
  editing.value = true
  Object.assign(form, {
    id: row.id, name: row.name, location: row.location || '',
    url: row.url, conf: row.conf, snapInterval: row.snapInterval, enabled: row.enabled,
    scheduleEnabled: row.scheduleEnabled, scheduleStart: row.scheduleStart, scheduleEnd: row.scheduleEnd,
  })
  dialogVisible.value = true
}
const submit = async () => {
  if (!form.name.trim() || !form.url.trim()) return ElMessage.warning('名称与地址不能为空')
  saving.value = true
  try {
    if (editing.value) {
      await updateCamera(form.id, { ...form })
      ElMessage.success('已更新')
    } else {
      await createCamera({ ...form })
      ElMessage.success('已新增')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    saving.value = false
  }
}

const start = async (row) => {
  try {
    await startCamera(row.id)
    ElMessage.success('已发起拉流，5秒内可见状态')
    load()
  } catch (e) { /* 拦截器已提示 */ }
}
const stop = async (row) => {
  await stopCamera(row.id)
  ElMessage.success('已停止')
  load()
}
const remove = async (row) => {
  await ElMessageBox.confirm(`确认删除「${row.name}」？正在拉流的会先被停止`, '提示', { type: 'warning' })
  await deleteCamera(row.id)
  ElMessage.success('已删除')
  load()
}

const formatGap = (sec) => {
  if (!sec || sec < 60) return `${sec || 0}s`
  if (sec < 3600) return `${Math.floor(sec / 60)}分`
  if (sec < 86400) return `${Math.floor(sec / 3600)}小时`
  return `${Math.floor(sec / 86400)}天`
}

onMounted(() => {
  load()
  pollTimer = setInterval(load, 5000)  // 每 5 秒刷新一次状态
})
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hint { color: #aaa; font-size: 12px; }
.url { color: #555; font-size: 12px; background: #f5f7fa; padding: 2px 6px; border-radius: 4px; word-break: break-all; }
.conf-val { font-weight: bold; color: #0a5a2c; margin-left: 8px; }
.dot {
  display: inline-block;
  width: 7px; height: 7px; border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}
.dot.online { background: #52c41a; box-shadow: 0 0 6px #52c41a; animation: blink 2s infinite; }
.dot.error { background: #f5222d; }
.dot.recent { background: #faad14; }
.dot.offline { background: #f5222d; }
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
