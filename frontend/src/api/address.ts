import axios from 'axios';

// ============ 收货地址相关 ============
export interface AddressItem {
  addressId: string;
  receiverName: string;
  receiverPhone: string;
  detailAddress: string;
  isDefault: boolean;
}

export function getAddressList() {
  return axios.get('/api/address/list');
}

export function addAddress(data: {
  receiverName: string;
  receiverPhone: string;
  detailAddress: string;
  isDefault?: boolean;
}) {
  return axios.post('/api/address/add', data);
}

export function updateAddress(data: {
  addressId: string;
  receiverName?: string;
  receiverPhone?: string;
  detailAddress?: string;
  isDefault?: boolean;
}) {
  return axios.post('/api/address/update', data);
}

export function deleteAddress(data: { addressId: string }) {
  return axios.post('/api/address/delete', data);
}
