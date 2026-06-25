<template>
  <div>
    <!-- 工地安全指数：顶部突出，但克制 -->
    <el-card class="score-card" style="margin-bottom: 20px">
      <el-row :gutter="32" align="middle">
        <el-col :span="7">
          <div class="score-block">
            <div class="score-eyebrow">今日工地安全指数</div>
            <div class="score-num" :style="{ color: scoreColor }">
              {{ score.score }}<span class="score-of">/100</span>
            </div>
            <div class="score-grade">
              <span class="score-dot" :style="{ background: scoreColor }"></span>
              <span class="score-grade-text">{{ score.grade }}</span>
            </div>
          </div>
        </el-col>
        <el-col :span="10">
          <div class="trend-wrap">
            <div class="trend-title">近 8 天趋势</div>
            <BaseChart v-if="score.trend?.length" :option="scoreTrendOption" style="height:120px" />
          </div>
        </el-col>
        <el-col :span="7">
          <div class="score-components">
            <div class="comp-item">
              <span class="comp-k">高危</span>
              <b class="comp-v danger">{{ score.components?.high || 0 }}</b>
            </div>
            <div class="comp-item">
              <span class="comp-k">中危</span>
              <b class="comp-v warn">{{ score.components?.mid || 0 }}</b>
            </div>
            <div class="comp-item">
              <span class="comp-k">已处理</span>
              <b class="comp-v ok">{{ score.components?.processed || 0 }}</b>
            </div>
            <div class="comp-item">
              <span class="comp-k">未处理</span>
              <b class="comp-v">{{ score.components?.pending || 0 }}</b>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 指标卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-num">{{ stats.total }}</div>
          <div class="stat-label">累计检测记录</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-num warn">{{ stats.pending }}</div>
          <div class="stat-label">待处理预警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-num danger">{{ stats.byRisk?.high || 0 }}</div>
          <div class="stat-label">高危事件</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-num">{{ classCount }}</div>
          <div class="stat-label">命中违规类别数</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-head">
              <span>近 7 天检测趋势</span>
              <el-button text type="primary" @click="loadStats">刷新</el-button>
            </div>
          </template>
          <BaseChart v-if="hasData" :option="trendOption" />
          <el-empty v-else description="暂无检测数据" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>违规类别分布</template>
          <BaseChart v-if="classCount" :option="classOption" />
          <el-empty v-else description="暂无检测数据，去「图片检测」上传一张试试" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>风险等级占比</template>
          <BaseChart v-if="hasData" :option="riskOption" />
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>检测来源分布</template>
          <BaseChart v-if="hasData" :option="typeOption" />
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 违规热力图：近 30 天 时段×类别 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>
            <div class="card-head">
              <span>违规热力图 · 近 30 天 时段 × 类别</span>
              <span class="hint">越红表示某时段某类违规越集中。可用于排班/巡检重点时段</span>
            </div>
          </template>
          <BaseChart v-if="heatData.data.length" :option="heatmapOption" style="height: 400px" />
          <el-empty v-else description="暂无足够数据生成热力图" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { fetchStats } from '@/api/records'
import { fetchSafetyScore, fetchHeatmap } from '@/api/reports'
import BaseChart from '@/components/BaseChart.vue'

const stats = reactive({ total: 0, pending: 0, byRisk: {}, byType: {}, byClass: {}, trend: [] })
const score = reactive({ score: 100, grade: '优秀', gradeColor: 'success', components: {}, trend: [] })
const heatData = ref({ xLabels: [], yLabels: [], data: [], max: 1 })
const classCount = computed(() => Object.keys(stats.byClass || {}).length)
const hasData = computed(() => stats.total > 0)

const GREEN = '#0a5a2c'
const scoreColor = computed(() => {
  if (score.score >= 95) return '#1abf80'
  if (score.score >= 85) return '#0a5a2c'
  if (score.score >= 70) return '#faad14'
  return '#f5222d'
})

const loadStats = async () => {
  try { Object.assign(stats, await fetchStats()) } catch (e) {}
  try { Object.assign(score, await fetchSafetyScore('day')) } catch (e) {}
  try {
    const h = await fetchHeatmap('hour', 30)
    let max = 1
    for (const [, , v] of h.data) if (v > max) max = v
    heatData.value = { ...h, max }
  } catch (e) {}
}

// 近 7 天趋势折线
const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['检测总数', '高危'] },
  grid: { left: 40, right: 20, top: 40, bottom: 30 },
  xAxis: { type: 'category', data: (stats.trend || []).map((t) => t.date) },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      name: '检测总数',
      type: 'line',
      smooth: true,
      data: (stats.trend || []).map((t) => t.total),
      itemStyle: { color: GREEN },
      areaStyle: { color: 'rgba(10,90,44,0.1)' },
    },
    {
      name: '高危',
      type: 'line',
      smooth: true,
      data: (stats.trend || []).map((t) => t.high),
      itemStyle: { color: '#f5222d' },
    },
  ],
}))

// 违规类别饼图
const classOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      data: Object.entries(stats.byClass || {}).map(([name, value]) => ({ name, value })),
      label: { formatter: '{b}: {c}' },
    },
  ],
}))

// 风险等级占比
const RISK_ZH = { high: '高危', mid: '中危', low: '低危' }
const RISK_COLOR = { high: '#f5222d', mid: '#faad14', low: '#52c41a' }
const riskOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      type: 'pie',
      radius: '60%',
      center: ['50%', '45%'],
      data: Object.entries(stats.byRisk || {}).map(([k, v]) => ({
        name: RISK_ZH[k] || k,
        value: v,
        itemStyle: { color: RISK_COLOR[k] },
      })),
    },
  ],
}))

// 安全指数 7 天趋势
const scoreTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 30, bottom: 30 },
  xAxis: { type: 'category', data: (score.trend || []).map((t) => t.date) },
  yAxis: { type: 'value', min: 0, max: 100 },
  series: [{
    type: 'line', smooth: true,
    data: (score.trend || []).map((t) => t.score),
    itemStyle: { color: scoreColor.value },
    areaStyle: { color: 'rgba(10,90,44,0.12)' },
    markLine: {
      symbol: 'none', silent: true,
      lineStyle: { color: '#ccc', type: 'dashed' },
      data: [{ yAxis: 85, label: { formatter: '良好 85', position: 'end' } }],
    },
  }],
}))

// 违规热力图（小时×类别，近 30 天）
const heatmapOption = computed(() => ({
  tooltip: {
    position: 'top',
    formatter: (p) => `${heatData.value.yLabels[p.data[1]]} · ${heatData.value.xLabels[p.data[0]]}：${p.data[2]} 次`,
  },
  grid: { left: 60, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: heatData.value.xLabels, splitArea: { show: true } },
  yAxis: { type: 'category', data: heatData.value.yLabels, splitArea: { show: true } },
  visualMap: {
    min: 0, max: heatData.value.max,
    calculable: true, orient: 'horizontal',
    left: 'center', bottom: 0,
    inRange: { color: ['#e8f5e9', '#0a5a2c', '#f5222d'] },
  },
  series: [{
    type: 'heatmap',
    data: heatData.value.data,
    label: { show: false },
    emphasis: { itemStyle: { shadowBlur: 6, shadowColor: 'rgba(0,0,0,0.4)' } },
  }],
}))

// 检测来源柱状
const TYPE_ZH = { img: '图片检测', video: '视频检测', camera: '实时检测' }
const typeOption = computed(() => {
  const entries = Object.entries(stats.byType || {})
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: entries.map(([k]) => TYPE_ZH[k] || k) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        barWidth: '40%',
        data: entries.map(([, v]) => v),
        itemStyle: { color: GREEN, borderRadius: [4, 4, 0, 0] },
      },
    ],
  }
})

onMounted(loadStats)
</script>

<style scoped>
.stat-card {
  text-align: left;
}
.stat-num {
  font-size: 32px;
  font-weight: 600;
  color: var(--text);
  font-family: var(--font-mono);
  letter-spacing: -1px;
}
.stat-num.warn { color: var(--warning); }
.stat-num.danger { color: var(--danger); }
.stat-label {
  margin-top: 4px;
  color: var(--text-3);
  font-size: 12px;
  letter-spacing: 0.3px;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint { color: #aaa; font-size: 12px; }
.score-card { background: var(--surface); }
.score-block { padding: 4px 0; }
.score-eyebrow {
  font-size: 12px;
  color: var(--text-3);
  font-weight: 500;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.score-num {
  font-size: 56px;
  font-weight: 600;
  font-family: var(--font-mono);
  line-height: 1;
  letter-spacing: -2px;
}
.score-of { font-size: 18px; color: var(--text-3); margin-left: 4px; font-weight: 400; }
.score-grade {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.score-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
}
.score-grade-text {
  font-size: 13px;
  color: var(--text-2);
  font-weight: 500;
}
.trend-wrap {
  border-left: 1px solid var(--divider);
  padding-left: 24px;
}
.trend-title {
  font-size: 12px;
  color: var(--text-3);
  font-weight: 500;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.score-components {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding-left: 24px;
  border-left: 1px solid var(--divider);
}
.comp-item {
  background: #fafbfc;
  padding: 10px 14px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--divider);
}
.comp-k {
  color: var(--text-2);
  font-size: 12px;
  font-weight: 500;
}
.comp-v {
  font-size: 20px;
  color: var(--text);
  font-family: var(--font-mono);
  font-weight: 600;
}
.comp-v.danger { color: var(--danger); }
.comp-v.warn { color: var(--warning); }
.comp-v.ok { color: var(--success); }
</style>
