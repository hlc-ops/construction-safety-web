<template>
  <div class="login-page">
    <!-- 左侧：品牌大图（布局沿用原版） -->
    <div class="left-section">
      <div class="brand">
        <div class="system-title">
          <img v-if="brand.logoUrl" :src="brand.logoUrl" class="brand-logo" alt="logo" />
          <span v-else>🏗️</span>
          {{ brand.name }}
        </div>
        <div class="system-subtitle">{{ brand.subtitle }}</div>
      </div>
    </div>

    <!-- 右侧：登录板块 -->
    <div class="right-section">
      <div class="login-box">
        <div class="login-header">
          <h2>欢迎回来</h2>
          <p>请登录您的账户以继续使用系统</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          size="large"
          @keyup.enter="onSubmit"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="success"
              class="login-btn"
              :loading="loading"
              @click="onSubmit"
            >
              立即登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="register-tip">
          还没有账户？<el-link type="success" :underline="false" @click="onRegister">立即注册</el-link>
        </div>
        <div class="hint">默认管理员账号：hlc / 123456</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/auth'
import { useBrandStore } from '@/store/brand'

const brand = useBrandStore()

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const onSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await login({ ...form })
      auth.setAuth(res.token, res.user)
      ElMessage.success('登录成功')
      router.push(route.query.redirect || '/')
    } catch (e) {
      // 错误提示已由 axios 拦截器统一处理
    } finally {
      loading.value = false
    }
  })
}

const onRegister = () => {
  ElMessage.info('注册功能将在后续开放')
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}

/* 左侧大图：深色叠层 + 克制的品牌 */
.left-section {
  flex: 1;
  background: url('/background.png') center / cover no-repeat;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-start;
  color: #fff;
  padding: 64px;
  position: relative;
  overflow: hidden;
}
.left-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(13, 31, 26, 0.4) 0%, rgba(13, 31, 26, 0.85) 100%);
}
.brand {
  position: relative;
  z-index: 1;
  text-align: left;
  max-width: 520px;
}
.system-title {
  font-size: 30px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  letter-spacing: 0.5px;
  line-height: 1.25;
}
.brand-logo {
  height: 44px;
  width: auto;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 4px 8px;
}
.system-subtitle {
  font-size: 15px;
  opacity: 0.85;
  line-height: 1.7;
  font-weight: 300;
  max-width: 460px;
}

/* 右侧登录板块 */
.right-section {
  width: 480px;
  background: var(--surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  border-left: 1px solid var(--border);
}
.login-box {
  width: 100%;
}
.login-header {
  margin-bottom: 36px;
}
.login-header h2 {
  color: var(--text);
  margin-bottom: 8px;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.login-header p {
  color: var(--text-2);
  font-size: 14px;
}
.login-btn {
  width: 100%;
  font-weight: 500;
  letter-spacing: 4px;
  height: 44px;
  font-size: 15px;
}
.register-tip {
  text-align: center;
  font-size: 13px;
  color: var(--text-3);
  margin-top: 12px;
}
.hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-3);
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid var(--divider);
}

@media (max-width: 768px) {
  .left-section {
    display: none;
  }
  .right-section {
    width: 100%;
  }
}
</style>
