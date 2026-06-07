import localeLogin from '@/views/login/locale/zh-CN';

import locale403 from '@/views/exception/403/locale/zh-CN';
import locale404 from '@/views/exception/404/locale/zh-CN';
import locale500 from '@/views/exception/500/locale/zh-CN';

import localeSettings from './zh-CN/settings';

export default {
  'menu.dashboard': '工作台',
  'menu.dish': '菜品管理',
  'menu.order': '订单管理',
  'menu.address': '地址管理',
  'navbar.action.locale': '切换为中文',
  'messageBox.logout': '退出登录',
  'messageBox.noContent': '暂无内容',
  ...localeSettings,
  ...localeLogin,
  ...locale403,
  ...locale404,
  ...locale500,
};
