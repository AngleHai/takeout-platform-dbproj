import axios from 'axios';

export function getUserList(params: {
  page?: number;
  pageSize?: number;
  keyword?: string;
  role?: string;
}) {
  return axios.get('/api/admin/users', { params });
}
