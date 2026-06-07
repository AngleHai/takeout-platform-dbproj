<template>
  <div class="container">
    <a-space direction="vertical" :size="16" fill>
      <a-card class="general-card" title="欢迎使用外卖平台管理系统">
        <a-result status="success" :title="`你好，${userStore.name || '用户'}`">
          <template #subtitle>
            <span>当前角色：{{ userStore.role }}</span>
          </template>
        </a-result>
      </a-card>

      <!-- 商家：待指派订单 -->
      <a-card v-if="userStore.role === '商家'" class="general-card" title="待指派配送的订单">
        <template #extra>
          <a-button type="text" @click="$router.push('/order/list')">查看全部订单</a-button>
        </template>
        <a-empty v-if="pendingOrders.length === 0" description="暂无待指派订单" />
        <a-list v-else :bordered="false">
          <a-list-item v-for="order in pendingOrders" :key="order.orderId">
            <a-list-item-meta
              :title="`订单 ${order.orderId}`"
              :description="`顾客：${order.customerName} | 金额：¥${order.orderAmount.toFixed(2)} | 下单时间：${order.orderTime}`"
            />
            <template #actions>
              <a-button type="primary" size="small" @click="$router.push('/order/list')">
                去指派送餐员
              </a-button>
            </template>
          </a-list-item>
        </a-list>
      </a-card>

      <!-- 送餐员：配送中的订单 -->
      <a-card v-if="userStore.role === '送餐员'" class="general-card" title="正在配送的订单">
        <template #extra>
          <a-button type="text" @click="$router.push('/order/list')">查看全部订单</a-button>
        </template>
        <a-empty v-if="deliveringOrders.length === 0" description="暂无配送中订单" />
        <a-list v-else :bordered="false">
          <a-list-item v-for="order in deliveringOrders" :key="order.orderId">
            <a-list-item-meta
              :title="`订单 ${order.orderId}`"
              :description="`顾客：${order.customerName} | 金额：¥${order.orderAmount.toFixed(2)} | 下单时间：${order.orderTime}`"
            />
            <template #actions>
              <a-button type="primary" size="small" @click="$router.push('/order/list')">
                去确认送达
              </a-button>
            </template>
          </a-list-item>
        </a-list>
      </a-card>

      <a-row :gutter="16">
        <a-col :span="8">
          <a-card class="general-card" title="快捷操作">
            <a-space direction="vertical" fill>
              <a-button v-if="userStore.role === '顾客' || userStore.role === '商家' || userStore.role === '管理员'" type="primary" long @click="$router.push('/dish/list')">
                <template #icon><icon-apps /></template>
                浏览菜品
              </a-button>
              <a-button long @click="$router.push('/order/list')">
                <template #icon><icon-file /></template>
                查看订单
              </a-button>
              <a-button long @click="$router.push('/address/list')" v-if="userStore.role === '顾客'">
                <template #icon><icon-location /></template>
                管理地址
              </a-button>
              <a-button long @click="$router.push('/user/list')" v-if="userStore.role === '管理员'">
                <template #icon><icon-user-group /></template>
                用户管理
              </a-button>
            </a-space>
          </a-card>
        </a-col>
        <a-col :span="16">
          <a-card class="general-card" title="系统说明">
            <a-list :bordered="false">
              <a-list-item>
                <a-typography-text bold>顾客</a-typography-text>
                ：浏览菜品、下单、管理收货地址、查看订单状态
              </a-list-item>
              <a-list-item>
                <a-typography-text bold>商家</a-typography-text>
                ：管理菜品（增删改）、查看订单、指派送餐员
              </a-list-item>
              <a-list-item>
                <a-typography-text bold>送餐员</a-typography-text>
                ：查看配送任务、确认送达
              </a-list-item>
            </a-list>
          </a-card>
        </a-col>
      </a-row>
    </a-space>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { useUserStore } from '@/store';
  import { getOrderList } from '@/api/order';

  const userStore = useUserStore();
  const pendingOrders = ref<any[]>([]);
  const deliveringOrders = ref<any[]>([]);

  async function fetchPendingOrders() {
    if (userStore.role === '商家') {
      const res: any = await getOrderList({ status: '已接单', pageSize: 5 });
      pendingOrders.value = res.list || [];
    }
    if (userStore.role === '送餐员') {
      const res: any = await getOrderList({ status: '配送中', pageSize: 5 });
      deliveringOrders.value = res.list || [];
    }
  }

  onMounted(() => {
    fetchPendingOrders();
  });
</script>

<script lang="ts">
  export default {
    name: 'Dashboard',
  };
</script>

<style lang="less" scoped>
  .container {
    background-color: var(--color-fill-2);
    padding: 16px 20px;
  }
  .general-card {
    border-radius: 4px;
  }
</style>
