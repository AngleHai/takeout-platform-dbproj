<template>
  <div class="container">
    <a-card class="general-card" title="用户管理">
      <template #extra>
        <a-space>
          <a-select v-model="roleFilter" placeholder="按角色筛选" allow-clear style="width: 120px" @change="fetchUsers">
            <a-option value="顾客">顾客</a-option>
            <a-option value="商家">商家</a-option>
            <a-option value="配送员">配送员</a-option>
            <a-option value="管理员">管理员</a-option>
          </a-select>
          <a-input-search
            v-model="keyword"
            placeholder="搜索用户名/ID"
            style="width: 200px"
            @search="fetchUsers"
          />
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data="userList"
        :pagination="pagination"
        :loading="loading"
        @page-change="onPageChange"
      >
        <template #role="{ record }">
          <a-tag :color="roleColor(record.role)">{{ record.role }}</a-tag>
        </template>
        <template #action="{ record }">
          <a-popconfirm
            content="确定要删除该用户吗？"
            @ok="handleDelete(record.userId)"
          >
            <a-button
              v-if="record.role !== '管理员'"
              type="text"
              status="danger"
              size="small"
            >
              删除
            </a-button>
          </a-popconfirm>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { getUserList, deleteUser } from '@/api/admin';

  const loading = ref(false);
  const userList = ref<any[]>([]);
  const keyword = ref('');
  const roleFilter = ref('');
  const pagination = reactive({ current: 1, pageSize: 20, total: 0 });

  const columns = [
    { title: '用户ID', dataIndex: 'userId', width: 100 },
    { title: '用户名', dataIndex: 'userName' },
    { title: '密码', dataIndex: 'password', width: 120 },
    { title: '电话', dataIndex: 'phone', width: 140 },
    { title: '角色', slotName: 'role', width: 100 },
    { title: '操作', slotName: 'action', width: 100 },
  ];

  function roleColor(role: string) {
    const map: Record<string, string> = {
      '顾客': 'blue',
      '商家': 'green',
      '配送员': 'orange',
      '管理员': 'red',
    };
    return map[role] || 'gray';
  }

  async function handleDelete(userId: string) {
    try {
      await deleteUser({ userId });
      Message.success('删除成功');
      fetchUsers();
    } catch (e) {
      // error handled by interceptor
    }
  }

  async function fetchUsers() {
    loading.value = true;
    try {
      const res: any = await getUserList({
        page: pagination.current,
        pageSize: pagination.pageSize,
        keyword: keyword.value || undefined,
        role: roleFilter.value || undefined,
      });
      userList.value = res.list;
      pagination.total = res.total;
    } finally {
      loading.value = false;
    }
  }

  function onPageChange(page: number) {
    pagination.current = page;
    fetchUsers();
  }

  onMounted(() => {
    fetchUsers();
  });
</script>

<script lang="ts">
  export default { name: 'UserList' };
</script>

<style scoped lang="less">
  .container {
    padding: 20px;
  }
</style>
