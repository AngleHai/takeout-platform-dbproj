import axios from 'axios';

// ============ 订单相关 ============
export interface OrderItem {
  orderId: string;
  customerId: string;
  merchantId: string;
  orderAmount: number;
  paymentMethod: string;
  orderTime: string;
  deliveryStatus: string;
  customerName: string;
  shopName: string;
}

export interface OrderListRes {
  list: OrderItem[];
  total: number;
}

export interface OrderDish {
  dishId: string;
  dishName: string;
  price: number;
  quantity: number;
}

export interface OrderDetail extends OrderItem {
  addressId: string;
  receiverName: string;
  receiverPhone: string;
  detailAddress: string;
  dishes: OrderDish[];
  logistics?: {
    deliverymanId: string;
    deliverymanName: string;
    estimatedTime: string;
    isDelivered: boolean;
    customerPhone: string;
  };
}

export function getOrderList(params: {
  page?: number;
  pageSize?: number;
  status?: string;
}) {
  return axios.get('/api/order/list', { params });
}

export function getOrderDetail(orderId: string) {
  return axios.get('/api/order/detail', { params: { orderId } });
}

export function createOrder(data: {
  merchantId: string;
  addressId: string;
  paymentMethod: string;
  dishes: { dishId: string; quantity: number }[];
}) {
  return axios.post('/api/order/create', data);
}

export function cancelOrder(data: { orderId: string }) {
  return axios.post('/api/order/cancel', data);
}

export function assignDelivery(data: {
  orderId: string;
  deliverymanId: string;
}) {
  return axios.post('/api/order/assign', data);
}

export function confirmDelivery(data: { orderId: string }) {
  return axios.post('/api/order/deliver', data);
}
