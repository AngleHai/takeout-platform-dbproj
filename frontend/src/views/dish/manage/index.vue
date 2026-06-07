<template>
  <div class="container">
    <a-card class="general-card" title="我的菜品管理">
      <template #extra>
        <a-button type="primary" @click="showAddModal">
          <template #icon><icon-plus /></template>
          添加菜品
        </a-button>
      </template>

      <a-table
        :columns="columns"
        :data="dishList"
        :pagination="pagination"
        :loading="loading"
        @page-change="onPageChange"
      >
        <template #price="{ record }">
          ¥{{ record.price.toFixed(2) }}
        </template>
        <template #action="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="showEditModal(record)">编辑</a-button>
            <a-popconfirm content="确认删除该菜品？" @ok="handleDelete(record.dishId)">
              <a-button type="text" status="danger" size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑对话框 -->
    <a-modal v-model:visible="modalVisible" :title="isEdit ? '编辑菜品' : '添加菜品'" @ok="handleSubmit">
      <a-form :model="form" layout="vertical">
        <a-form-item label="菜品名称" required>
          <a-input v-model="form.dishName" placeholder="请输入菜品名称" />
        </a-form-item>
        <a-form-item label="价格" required>
          <a-input-number v-model="form.price" :min="0.01" :precision="2" placeholder="请输入价格" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { getDishList, addDish, updateDish, deleteDish } from '@/api/dish';
  import { useUserStore } from '@/store';

  const userStore = useUserStore();
  const loading = ref(false);
  const dishList = ref<any[]>([]);
  const pagination = reactive({ current: 1, pageSize: 10, total: 0 });
  const modalVisible = ref(false);
  const isEdit = ref(false);
  const form = reactive({ dishId: '', dishName: '', price: 0 });

  const columns = [
    { title: '菜品ID', dataIndex: 'dishId', width: 100 },
    { title: '菜品名称', dataIndex: 'dishName' },
    { title: '价格', slotName: 'price', width: 100 },
    { title: '销量', dataIndex: 'totalSales', width: 80 },
    { title: '操作', slotName: 'action', width: 150 },
  ];

  async function fetchDishes() {
    loading.value = true;
    try {
      const res: any = await getDishList({
        merchantId: userStore.userId,
        page: pagination.current,
        pageSize: pagination.pageSize,
      });
      dishList.value = res.list;
      pagination.total = res.total;
    } finally {
      loading.value = false;
    }
  }

  function onPageChange(page: number) {
    pagination.current = page;
    fetchDishes();
  }

  function showAddModal() {
    isEdit.value = false;
    form.dishId = '';
    form.dishName = '';
    form.price = 0;
    modalVisible.value = true;
  }

  function showEditModal(record: any) {
    isEdit.value = true;
    form.dishId = record.dishId;
    form.dishName = record.dishName;
    form.price = record.price;
    modalVisible.value = true;
  }

  async function handleSubmit() {
    if (!form.dishName || form.price <= 0) {
      Message.warning('请填写完整信息');
      return;
    }
    try {
      if (isEdit.value) {
        await updateDish({ dishId: form.dishId, dishName: form.dishName, price: form.price });
        Message.success('修改成功');
      } else {
        await addDish({ dishName: form.dishName, price: form.price });
        Message.success('添加成功');
      }
      modalVisible.value = false;
      fetchDishes();
    } catch (e) {
      // handled by interceptor
    }
  }

  async function handleDelete(dishId: string) {
    try {
      await deleteDish({ dishId });
      Message.success('删除成功');
      fetchDishes();
    } catch (e) {
      // handled by interceptor
    }
  }

  onMounted(() => {
    fetchDishes();
  });
</script>

<script lang="ts">
  export default { name: 'DishManage' };
</script>

<style scoped lang="less">
  .container {
    padding: 20px;
  }
</style>
