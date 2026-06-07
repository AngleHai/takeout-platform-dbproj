<template>
  <div class="login-form-wrapper">
    <div class="login-form-title">注册账号</div>
    <div class="login-form-sub-title">外卖平台管理系统</div>
    <div class="login-form-error-msg">{{ errorMessage }}</div>
    <a-form
      ref="regForm"
      :model="formData"
      class="login-form"
      layout="vertical"
      @submit="handleSubmit"
    >
      <a-form-item
        field="username"
        :rules="[{ required: true, message: '用户名不能为空' }]"
        hide-label
      >
        <a-input v-model="formData.username" placeholder="用户名">
          <template #prefix><icon-user /></template>
        </a-input>
      </a-form-item>
      <a-form-item
        field="password"
        :rules="[
          { required: true, message: '密码不能为空' },
          { minLength: 6, message: '密码至少6位' },
        ]"
        hide-label
      >
        <a-input-password v-model="formData.password" placeholder="密码（至少6位）" allow-clear>
          <template #prefix><icon-lock /></template>
        </a-input-password>
      </a-form-item>
      <a-form-item
        field="role"
        :rules="[{ required: true, message: '请选择角色' }]"
        hide-label
      >
        <a-select v-model="formData.role" placeholder="选择角色">
          <a-option value="顾客">顾客</a-option>
          <a-option value="商家">商家</a-option>
          <a-option value="送餐员">送餐员</a-option>
        </a-select>
      </a-form-item>
      <a-form-item
        field="phone"
        :rules="[{ match: /^1\d{10}$/, message: '请输入11位手机号' }]"
        hide-label
      >
        <a-input v-model="formData.phone" placeholder="手机号（选填）">
          <template #prefix><icon-phone /></template>
        </a-input>
      </a-form-item>

      <!-- 顾客额外字段 -->
      <template v-if="formData.role === '顾客'">
        <a-form-item field="name" hide-label>
          <a-input v-model="formData.name" placeholder="姓名（选填）" />
        </a-form-item>
      </template>

      <!-- 商家额外字段 -->
      <template v-if="formData.role === '商家'">
        <a-form-item
          field="shopName"
          :rules="[{ required: true, message: '店铺名称不能为空' }]"
          hide-label
        >
          <a-input v-model="formData.shopName" placeholder="店铺名称" />
        </a-form-item>
      </template>

      <a-space :size="16" direction="vertical">
        <a-button type="primary" html-type="submit" long :loading="loading">
          注册
        </a-button>
        <a-button type="text" long class="login-form-register-btn" @click="$emit('switchToLogin')">
          已有账号？返回登录
        </a-button>
      </a-space>
    </a-form>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { ValidatedError } from '@arco-design/web-vue/es/form/interface';
  import { register } from '@/api/user';
  import useLoading from '@/hooks/loading';

  const emit = defineEmits(['switchToLogin']);

  const errorMessage = ref('');
  const { loading, setLoading } = useLoading();

  const formData = reactive({
    username: '',
    password: '',
    role: '',
    phone: '',
    name: '',
    shopName: '',
  });

  const handleSubmit = async ({
    errors,
  }: {
    errors: Record<string, ValidatedError> | undefined;
    values: Record<string, any>;
  }) => {
    if (loading.value) return;
    if (!errors) {
      setLoading(true);
      errorMessage.value = '';
      try {
        await register({
          username: formData.username,
          password: formData.password,
          role: formData.role,
          phone: formData.phone || undefined,
          name: formData.name || undefined,
          shopName: formData.shopName || undefined,
        });
        Message.success('注册成功，请登录');
        emit('switchToLogin');
      } catch (err) {
        errorMessage.value = (err as Error).message;
      } finally {
        setLoading(false);
      }
    }
  };
</script>

<style lang="less" scoped>
  .login-form {
    &-wrapper {
      width: 320px;
    }

    &-title {
      color: var(--color-text-1);
      font-weight: 500;
      font-size: 24px;
      line-height: 32px;
    }

    &-sub-title {
      color: var(--color-text-3);
      font-size: 16px;
      line-height: 24px;
    }

    &-error-msg {
      height: 32px;
      color: rgb(var(--red-6));
      line-height: 32px;
    }

    &-register-btn {
      color: var(--color-text-3) !important;
    }
  }
</style>
