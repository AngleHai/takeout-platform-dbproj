import axios from 'axios';

// ============ 菜品相关 ============
export interface DishItem {
  dishId: string;
  dishName: string;
  price: number;
  totalSales: number;
  merchantId: string;
  shopName: string;
}

export interface DishListRes {
  list: DishItem[];
  total: number;
}

export function getDishList(params: {
  merchantId?: string;
  keyword?: string;
  page?: number;
  pageSize?: number;
}) {
  return axios.get('/api/dish/list', { params });
}

export function addDish(data: { dishName: string; price: number }) {
  return axios.post('/api/dish/add', data);
}

export function updateDish(data: {
  dishId: string;
  dishName?: string;
  price?: number;
}) {
  return axios.post('/api/dish/update', data);
}

export function deleteDish(data: { dishId: string }) {
  return axios.post('/api/dish/delete', data);
}
