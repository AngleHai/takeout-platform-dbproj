<template>
  <div class="container">
    <a-card class="general-card" title="菜品列表">
      <template #extra>
        <a-space>
          <a-select
            v-model="selectedShop"
            placeholder="全部店铺"
            allow-clear
            style="width: 160px"
            @change="onShopChange"
          >
            <a-option v-for="shop in shopList" :key="shop.merchantId" :value="shop.merchantId">
              {{ shop.shopName }}
            </a-option>
          </a-select>
          <a-input-search
            v-model="searchKeyword"
            placeholder="搜索菜品"
            style="width: 200px"
            @search="fetchDishes"
          />
          <a-badge v-if="userStore.role === '顾客'" :count="cart.length">
            <a-button type="primary" @click="openCart">
              <template #icon><icon-shopping-cart /></template>
              去下单
            </a-button>
          </a-badge>
        </a-space>
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
          <template v-if="userStore.role === '顾客'">
            <a-input-number
              v-if="getCartQty(record.dishId) > 0"
              :model-value="getCartQty(record.dishId)"
              :min="0"
              :max="99"
              size="small"
              style="width: 120px"
              @change="(val: number) => setCartQty(record, val)"
            />
            <a-button
              v-else
              type="primary"
              size="small"
              @click="handleAddToCart(record)"
            >
              加入购物车
            </a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 下单对话框 -->
    <a-modal v-model:visible="cartVisible" title="确认下单" :width="520" @ok="handleSubmitOrder">
      <a-form :model="orderForm">
        <a-form-item label="已选菜品">
          <div class="cart-list">
            <div v-for="item in cart" :key="item.dishId" class="cart-item">
              <span class="cart-item-name">{{ item.dishName }}</span>
              <div class="cart-item-ctrl">
                <a-input-number
                  :model-value="item.quantity"
                  :min="1"
                  :max="99"
                  size="mini"
                  style="width: 100px"
                  @change="(val: number) => setQty(item, val)"
                />
              </div>
              <span class="cart-item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
              <a-button size="mini" type="text" status="danger" @click="removeFromCart(item)">
                删除
              </a-button>
            </div>
          </div>
        </a-form-item>
        <a-divider style="margin: 4px 0 12px" />
        <div style="text-align: right; margin-bottom: 16px">
          <strong>合计：¥{{ cartTotal.toFixed(2) }}</strong>
        </div>
        <a-form-item label="收货地址">
          <a-select v-model="orderForm.addressId" placeholder="选择地址">
            <a-option v-for="addr in addresses" :key="addr.addressId" :value="addr.addressId">
              {{ addr.receiverName }} - {{ addr.detailAddress }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="支付方式">
          <a-select v-model="orderForm.paymentMethod" placeholder="选择支付方式">
            <a-option value="微信支付">微信支付</a-option>
            <a-option value="支付宝">支付宝</a-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { getDishList, getShopList } from '@/api/dish';
  import { createOrder } from '@/api/order';
  import { getAddressList } from '@/api/address';
  import { useUserStore } from '@/store';

  const userStore = useUserStore();
  const loading = ref(false);
  const dishList = ref<any[]>([]);
  const searchKeyword = ref('');
  const selectedShop = ref('');
  const shopList = ref<any[]>([]);
  const pagination = reactive({ current: 1, pageSize: 10, total: 0 });

  const columns = [
    { title: '菜品名称', dataIndex: 'dishName' },
    { title: '价格', slotName: 'price' },
    { title: '销量', dataIndex: 'totalSales' },
    { title: '店铺', dataIndex: 'shopName' },
    { title: '操作', slotName: 'action', width: 160 },
  ];

  // 购物车
  const cart = ref<any[]>([]);
  const cartVisible = ref(false);
  const addresses = ref<any[]>([]);
  const orderForm = reactive({ addressId: '', paymentMethod: '微信支付' });

  const cartTotal = computed(() =>
    cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  async function fetchDishes() {
    loading.value = true;
    try {
      const res: any = await getDishList({
        merchantId: selectedShop.value || undefined,
        keyword: searchKeyword.value,
        page: pagination.current,
        pageSize: pagination.pageSize,
      });
      dishList.value = res.list;
      pagination.total = res.total;
    } finally {
      loading.value = false;
    }
  }

  function onShopChange() {
    pagination.current = 1;
    fetchDishes();
  }

  function onPageChange(page: number) {
    pagination.current = page;
    fetchDishes();
  }

  function handleAddToCart(dish: any) {
    const existing = cart.value.find((d) => d.dishId === dish.dishId);
    if (existing) {
      if (cart.value.length > 0 && cart.value[0].merchantId !== dish.merchantId) {
        Message.warning('只能选择同一商家的菜品');
        return;
      }
      existing.quantity += 1;
    } else {
      if (cart.value.length > 0 && cart.value[0].merchantId !== dish.merchantId) {
        Message.warning('只能选择同一商家的菜品，已清空购物车');
        cart.value = [];
      }
      cart.value.push({ ...dish, quantity: 1 });
    }
    Message.success(`已添加 ${dish.dishName}`);
  }

  function changeQty(item: any, delta: number) {
    item.quantity += delta;
    if (item.quantity <= 0) {
      removeFromCart(item);
    }
  }

  function removeFromCart(item: any) {
    cart.value = cart.value.filter((d) => d.dishId !== item.dishId);
    if (cart.value.length === 0) {
      cartVisible.value = false;
    }
  }

  function getCartQty(dishId: string) {
    const item = cart.value.find((d) => d.dishId === dishId);
    return item ? item.quantity : 0;
  }

  function changeCartQty(dish: any, delta: number) {
    const existing = cart.value.find((d) => d.dishId === dish.dishId);
    if (existing) {
      existing.quantity += delta;
      if (existing.quantity <= 0) {
        cart.value = cart.value.filter((d) => d.dishId !== dish.dishId);
      }
    }
  }

  function setCartQty(dish: any, val: number) {
    if (val <= 0) {
      cart.value = cart.value.filter((d) => d.dishId !== dish.dishId);
    } else {
      const existing = cart.value.find((d) => d.dishId === dish.dishId);
      if (existing) {
        existing.quantity = val;
      }
    }
  }

  function setQty(item: any, val: number) {
    if (val <= 0) {
      removeFromCart(item);
    } else {
      item.quantity = val;
    }
  }

  async function handleSubmitOrder() {
    if (cart.value.length === 0) {
      Message.warning('购物车为空');
      return;
    }
    if (!orderForm.addressId) {
      Message.warning('请选择收货地址');
      return;
    }
    try {
      await createOrder({
        merchantId: cart.value[0].merchantId,
        addressId: orderForm.addressId,
        paymentMethod: orderForm.paymentMethod,
        dishes: cart.value.map((d) => ({ dishId: d.dishId, quantity: d.quantity })),
      });
      Message.success('下单成功');
      cart.value = [];
      cartVisible.value = false;
    } catch (e) {
      // error handled by interceptor
    }
  }

  async function openCart() {
    if (cart.value.length === 0) {
      Message.warning('购物车为空');
      return;
    }
    // 加载地址
    const res: any = await getAddressList();
    addresses.value = res;
    cartVisible.value = true;
  }

  async function fetchShops() {
    const res: any = await getShopList();
    shopList.value = res;
  }

  onMounted(() => {
    fetchShops();
    fetchDishes();
  });
</script>

<script lang="ts">
  export default { name: 'DishList' };
</script>

<style scoped lang="less">
  .container {
    padding: 20px;
  }

  .cart-list {
    width: 100%;
  }

  .cart-item {
    display: flex;
    align-items: center;
    padding: 6px 0;
    line-height: 1.5;
  }

  .cart-item-name {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .cart-item-ctrl {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
    margin: 0 12px;
  }

  .cart-item-qty {
    width: 24px;
    text-align: center;
    flex-shrink: 0;
  }

  .cart-item-price {
    width: 80px;
    text-align: right;
    flex-shrink: 0;
  }
</style>
