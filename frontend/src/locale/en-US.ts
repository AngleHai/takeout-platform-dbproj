import localeLogin from '@/views/login/locale/en-US';

import locale403 from '@/views/exception/403/locale/en-US';
import locale404 from '@/views/exception/404/locale/en-US';
import locale500 from '@/views/exception/500/locale/en-US';

import localeSettings from './en-US/settings';

export default {
  'menu.dashboard': 'Dashboard',
  'menu.dish': 'Dishes',
  'menu.order': 'Orders',
  'menu.address': 'Addresses',
  'navbar.action.locale': 'Switch to English',
  'messageBox.logout': 'Logout',
  'messageBox.noContent': 'No content',
  ...localeSettings,
  ...localeLogin,
  ...locale403,
  ...locale404,
  ...locale500,
};
