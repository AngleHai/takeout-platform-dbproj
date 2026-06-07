import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const ADDRESS: AppRouteRecordRaw = {
  path: '/address',
  name: 'address',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: '地址管理',
    requiresAuth: true,
    icon: 'icon-location',
    order: 3,
    roles: ['顾客'],
  },
  children: [
    {
      path: 'list',
      name: 'AddressList',
      component: () => import('@/views/address/index.vue'),
      meta: {
        locale: '我的地址',
        requiresAuth: true,
        roles: ['顾客'],
      },
    },
  ],
};

export default ADDRESS;
