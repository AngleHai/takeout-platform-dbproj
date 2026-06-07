import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const DISH: AppRouteRecordRaw = {
  path: '/dish',
  name: 'dish',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: '菜品管理',
    requiresAuth: true,
    icon: 'icon-apps',
    order: 1,
    roles: ['顾客', '商家', '管理员'],
  },
  children: [
    {
      path: 'list',
      name: 'DishList',
      component: () => import('@/views/dish/list/index.vue'),
      meta: {
        locale: '浏览菜品',
        requiresAuth: true,
        roles: ['顾客', '商家', '管理员'],
      },
    },
    {
      path: 'manage',
      name: 'DishManage',
      component: () => import('@/views/dish/manage/index.vue'),
      meta: {
        locale: '我的菜品',
        requiresAuth: true,
        roles: ['商家'],
      },
    },
  ],
};

export default DISH;
