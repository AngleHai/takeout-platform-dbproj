import axios from 'axios';

export function getUserList(params: {
  page?: number;
  pageSize?: number;
  keyword?: string;
  role?: string;
}) {
  return axios.get('/api/admin/users', { params });
}

export function deleteUser(data: { userId: string }) {
  return axios.post('/api/admin/delete-user', data);
}
