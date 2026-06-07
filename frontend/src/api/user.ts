import axios from 'axios';
import { UserState } from '@/store/modules/user/types';

export interface LoginData {
  username: string;
  password: string;
}

export interface LoginRes {
  token: string;
  userInfo: UserState;
}

export function login(data: LoginData): Promise<LoginRes> {
  return axios.post('/api/user/login', data);
}

export function register(data: {
  username: string;
  password: string;
  phone?: string;
  role: string;
  name?: string;
  gender?: string;
  age?: number;
  email?: string;
  shopName?: string;
}) {
  return axios.post('/api/user/register', data);
}

export function logout(): Promise<void> {
  return axios.post('/api/user/logout');
}

export function getUserInfo(): Promise<UserState> {
  return axios.post('/api/user/info');
}
