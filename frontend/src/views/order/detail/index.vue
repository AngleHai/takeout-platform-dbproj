<template>
  <div class="container">
    <a-card class="general-card" title="订单详情" :loading="loading">
      <template #extra>
        <a-button @click="$router.back()">返回</a-button>
      </template>

      <a-descriptions :column="2" bordered v-if="order">
        <a-descriptions-item label="订单ID">{{ order.orderId }}</a-descriptions-item>
        <a-descriptions-item label="下单时间">{{ order.orderTime }}</a-descriptions-item>
        <a-descriptions-item label="顾客">{{ order.customerName }}</a-descriptions-item>
        <a-descriptions-item label="店铺">{{ order.shopName }}</a-descriptions-item>
        <a-descriptions-item label="订单金额">¥{{ order.orderAmount?.toFixed(2) }}</a-descriptions-item>
        <a-descriptions-item label="支付方式">{{ order.paymentMethod }}</a-descriptions-item>
        <a-descriptions-item label="配送状态">
          <a-tag :color="statusColor(order.deliveryStatus)">{{ order.deliveryStatus }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="收货地址">
          {{ order.receiverName }} {{ order.receiverPhone }}<br/>
          {{ order.detailAddress }}
        </a-descriptions-item>
      </a-descriptions>

      <a-divider>菜品明细</a-divider>
      <a-table :columns="dishColumns" :data="order?.dishes || []" :pagination="false" size="small">
        <template #price="{ record }">¥{{ record.price.toFixed(2) }}</template>
        <template #subtotal="{ record }">¥{{ (record.price * record.quantity).toFixed(2) }}</template>
      </a-table>

      <template v-if="order?.logistics">
        <a-divider>配送信息</a-divider>
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="配送员">{{ order.logistics.deliverymanName }}</a-descriptions-item>
          <a-descriptions-item label="预计送达">{{ order.logistics.estimatedTime }}</a-descriptions-item>
          <a-descriptions-item label="顾客电话">{{ order.logistics.customerPhone }}</a-descriptions-item>
          <a-descriptions-item label="是否送达">
            <a-tag :color="order.logistics.isDelivered ? 'green' : 'orange'">
              {{ order.logistics.isDelivered ? '已送达' : '配送中' }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>
      </template>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import { getOrderDetail } from '@/api/order';

  const route = useRoute();
  const loading = ref(false);
  const order = ref<any>(null);

  const dishColumns = [
    { title: '菜品', dataIndex: 'dishName' },
    { title: '单价', slotName: 'price', width: 100 },
    { title: '数量', dataIndex: 'quantity', width: 80 },
    { title: '小计', slotName: 'subtotal', width: 100 },
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

  async function fetchDetail() {
    const orderId = route.query.orderId as string;
    if (!orderId) return;
    loading.value = true;
    try {
      const res: any = await getOrderDetail(orderId);
      order.value = res;
    } finally {
      loading.value = false;
    }
  }

  onMounted(() => {
    fetchDetail();
  });
</script>

<script lang="ts">
  export default { name: 'OrderDetail' };
</script>

<style scoped lang="less">
  .container {
    padding: 20px;
  }
</style>
