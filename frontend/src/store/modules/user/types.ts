export type RoleType = '' | '*' | '顾客' | '商家' | '送餐员' | '管理员';
export interface UserState {
  name?: string;
  userId?: string;
  role: RoleType;
  phone?: string;
  shopName?: string;
  workStatus?: string;
}
