<template>
  <div class="container">
    <a-card class="general-card" title="订单列表">
      <template #extra>
        <a-space>
          <a-select v-model="statusFilter" placeholder="筛选状态" allow-clear style="width: 140px" @change="fetchOrders">
            <a-option value="已接单">已接单</a-option>
            <a-option value="配送中">配送中</a-option>
            <a-option value="已完成">已完成</a-option>
            <a-option value="已取消">已取消</a-option>
          </a-select>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data="orderList"
        :pagination="pagination"
        :loading="loading"
        @page-change="onPageChange"
      >
        <template #orderAmount="{ record }">
          ¥{{ record.orderAmount.toFixed(2) }}
        </template>
        <template #deliveryStatus="{ record }">
          <a-tag :color="statusColor(record.deliveryStatus)">
            {{ record.deliveryStatus }}
          </a-tag>
        </template>
        <template #action="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="goDetail(record.orderId)">详情</a-button>
            <a-popconfirm
              v-if="userStore.role === '顾客' && record.deliveryStatus === '已接单'"
              content="确认取消订单？"
              @ok="handleCancel(record.orderId)"
            >
              <a-button type="text" status="danger" size="small">取消</a-button>
            </a-popconfirm>
            <a-button
              v-if="userStore.role === '商家' && record.deliveryStatus === '已接单'"
              type="text" size="small"
              @click="showAssignModal(record.orderId)"
            >
              指派配送
            </a-button>
            <a-popconfirm
              v-if="userStore.role === '送餐员' && record.deliveryStatus === '配送中'"
              content="确认已送达？"
              @ok="handleDeliver(record.orderId)"
            >
              <a-button type="text" status="success" size="small">确认送达</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 指派送餐员对话框 -->
    <a-modal v-model:visible="assignVisible" title="指派送餐员" @ok="handleAssign">
      <a-form-item label="选择送餐员">
        <a-select v-model="assignForm.deliverymanId" placeholder="选择空闲送餐员">
          <a-option v-for="dm in deliverymen" :key="dm.userId" :value="dm.userId">
            {{ dm.name }} ({{ dm.workStatus }})
          </a-option>
        </a-select>
      </a-form-item>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { Message } from '@arco-design/web-vue';
  import { getOrderList, cancelOrder, assignDelivery, confirmDelivery } from '@/api/order';
  import { useUserStore } from '@/store';
  import axios from 'axios';

  const router = useRouter();
  const userStore = useUserStore();
  const loading = ref(false);
  const orderList = ref<any[]>([]);
  const statusFilter = ref('');
  const pagination = reactive({ current: 1, pageSize: 10, total: 0 });

  // 指派
  const assignVisible = ref(false);
  const assignForm = reactive({ orderId: '', deliverymanId: '' });
  const deliverymen = ref<any[]>([]);

  const columns = [
    { title: '订单ID', dataIndex: 'orderId', width: 100 },
    { title: '顾客', dataIndex: 'customerName', width: 80 },
    { title: '店铺', dataIndex: 'shopName' },
    { title: '金额', slotName: 'orderAmount', width: 100 },
    { title: '下单时间', dataIndex: 'orderTime', width: 170 },
    { title: '状态', slotName: 'deliveryStatus', width: 100 },
    { title: '操作', slotName: 'action', width: 200 },
  ];

  function statusColor(status: string) {
    const map: Record<string, string> = {
      '已接单': 'blue',
      '配送中': 'orange',
      '已完成': 'green',
      '已取消': 'red',
    };
    return map[status] || 'gray';
  }

  async function fetchOrders() {
    loading.value = true;
    try {
      const res: any = await getOrderList({
        page: pagination.current,
        pageSize: pagination.pageSize,
        status: statusFilter.value || undefined,
      });
      orderList.value = res.list;
      pagination.total = res.total;
    } finally {
      loading.value = false;
    }
  }

  function onPageChange(page: number) {
    pagination.current = page;
    fetchOrders();
  }

  function goDetail(orderId: string) {
    router.push({ path: '/order/detail', query: { orderId } });
  }

  async function handleCancel(orderId: string) {
    await cancelOrder({ orderId });
    Message.success('取消成功');
    fetchOrders();
  }

  async function showAssignModal(orderId: string) {
    assignForm.orderId = orderId;
    assignForm.deliverymanId = '';
    // 获取空闲送餐员列表
    const res: any = await axios.get('/api/deliveryman/available');
    deliverymen.value = res || [];
    assignVisible.value = true;
  }

  async function handleAssign() {
    if (!assignForm.deliverymanId) {
      Message.warning('请选择送餐员');
      return;
    }
    await assignDelivery({ orderId: assignForm.orderId, deliverymanId: assignForm.deliverymanId });
    Message.success('指派成功');
    assignVisible.value = false;
    fetchOrders();
  }

  async function handleDeliver(orderId: string) {
    await confirmDelivery({ orderId });
    Message.success('确认送达');
    fetchOrders();
  }

  onMounted(() => {
    fetchOrders();
  });
</script>

<script lang="ts">
  export default { name: 'OrderList' };
</script>

<style scoped lang="less">
  .container {
    padding: 20px;
  }
</style>
