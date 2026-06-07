<script lang="ts" setup>
  import { useRoute, useRouter } from 'vue-router';

  const route = useRoute();
  const router = useRouter();

  const { params, query } = route;
  const { path } = params;

  router.replace({
    path: `/${Array.isArray(path) ? path.join('/') : path}`,
    query,
  });
</script>
