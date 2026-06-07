<template>
  <div class="container">
    <a-card class="general-card" title="我的收货地址">
      <template #extra>
        <a-button type="primary" @click="showAddModal">
          <template #icon><icon-plus /></template>
          添加地址
        </a-button>
      </template>

      <a-list :bordered="false" :loading="loading">
        <a-list-item v-for="addr in addressList" :key="addr.addressId">
          <a-list-item-meta>
            <template #title>
              <a-space>
                <span>{{ addr.receiverName }}</span>
                <span>{{ addr.receiverPhone }}</span>
                <a-tag v-if="addr.isDefault" color="green" size="small">默认</a-tag>
              </a-space>
            </template>
            <template #description>
              {{ addr.detailAddress }}
            </template>
          </a-list-item-meta>
          <template #actions>
            <a-button type="text" size="small" @click="showEditModal(addr)">编辑</a-button>
            <a-popconfirm content="确认删除该地址？" @ok="handleDelete(addr.addressId)">
              <a-button type="text" status="danger" size="small">删除</a-button>
            </a-popconfirm>
          </template>
        </a-list-item>
      </a-list>
    </a-card>

    <!-- 添加/编辑对话框 -->
    <a-modal v-model:visible="modalVisible" :title="isEdit ? '编辑地址' : '添加地址'" @ok="handleSubmit">
      <a-form :model="form" layout="vertical">
        <a-form-item label="收货人" required>
          <a-input v-model="form.receiverName" placeholder="请输入收货人姓名" />
        </a-form-item>
        <a-form-item label="联系电话" required>
          <a-input v-model="form.receiverPhone" placeholder="请输入电话" />
        </a-form-item>
        <a-form-item label="详细地址" required>
          <a-textarea v-model="form.detailAddress" placeholder="请输入详细地址" />
        </a-form-item>
        <a-form-item label="设为默认">
          <a-switch v-model="form.isDefault" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { getAddressList, addAddress, updateAddress, deleteAddress } from '@/api/address';

  const loading = ref(false);
  const addressList = ref<any[]>([]);
  const modalVisible = ref(false);
  const isEdit = ref(false);
  const form = reactive({
    addressId: '',
    receiverName: '',
    receiverPhone: '',
    detailAddress: '',
    isDefault: false,
  });

  async function fetchAddresses() {
    loading.value = true;
    try {
      const res: any = await getAddressList();
      addressList.value = res;
    } finally {
      loading.value = false;
    }
  }

  function showAddModal() {
    isEdit.value = false;
    form.addressId = '';
    form.receiverName = '';
    form.receiverPhone = '';
    form.detailAddress = '';
    form.isDefault = false;
    modalVisible.value = true;
  }

  function showEditModal(addr: any) {
    isEdit.value = true;
    form.addressId = addr.addressId;
    form.receiverName = addr.receiverName;
    form.receiverPhone = addr.receiverPhone;
    form.detailAddress = addr.detailAddress;
    form.isDefault = addr.isDefault;
    modalVisible.value = true;
  }

  async function handleSubmit() {
    if (!form.receiverName || !form.receiverPhone || !form.detailAddress) {
      Message.warning('请填写完整信息');
      return;
    }
    try {
      if (isEdit.value) {
        await updateAddress({
          addressId: form.addressId,
          receiverName: form.receiverName,
          receiverPhone: form.receiverPhone,
          detailAddress: form.detailAddress,
          isDefault: form.isDefault,
        });
        Message.success('修改成功');
      } else {
        await addAddress({
          receiverName: form.receiverName,
          receiverPhone: form.receiverPhone,
          detailAddress: form.detailAddress,
          isDefault: form.isDefault,
        });
        Message.success('添加成功');
      }
      modalVisible.value = false;
      fetchAddresses();
    } catch (e) {
      // handled by interceptor
    }
  }

  async function handleDelete(addressId: string) {
    try {
      await deleteAddress({ addressId });
      Message.success('删除成功');
      fetchAddresses();
    } catch (e) {
      // handled by interceptor
    }
  }

  onMounted(() => {
    fetchAddresses();
  });
</script>

<script lang="ts">
  export default { name: 'AddressList' };
</script>

<style scoped lang="less">
  .container {
    padding: 20px;
  }
</style>
