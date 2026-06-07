import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const ORDER: AppRouteRecordRaw = {
  path: '/order',
  name: 'order',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: '订单管理',
    requiresAuth: true,
    icon: 'icon-file',
    order: 2,
    roles: ['顾客', '商家', '配送员', '管理员'],
  },
  children: [
    {
      path: 'list',
      name: 'OrderList',
      component: () => import('@/views/order/list/index.vue'),
      meta: {
        locale: '订单列表',
        requiresAuth: true,
      },
    },
    {
      path: 'detail',
      name: 'OrderDetail',
      component: () => import('@/views/order/detail/index.vue'),
      meta: {
        locale: '订单详情',
        requiresAuth: true,
        hideInMenu: true,
      },
    },
  ],
};

export default ORDER;
