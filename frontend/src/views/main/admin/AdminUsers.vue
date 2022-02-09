<template>
  <div>
    <v-toolbar light>
      <v-toolbar-title>
        Manage Users
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" to="/main/admin/users/create">Create User</v-btn>
    </v-toolbar>
    <v-data-table
    :headers="headers"
    :items="users"
    >
      <template
      v-slot:item.disabled="{item}"
      >
        <v-simple-checkbox
          v-model="!item.disabled"
          disabled>
        </v-simple-checkbox>
      </template>
      <template
        v-slot:item.isSuperuser="{item}"
        >
        <v-simple-checkbox
          v-model="item.isSuperuser"
          disabled>
        </v-simple-checkbox>
      </template>
      <template
        v-slot:item.id="{item}"
        >
        <v-btn
            icon
          v-model="item.id"
          :to="{name:'main-admin-users-edit', params:{id: item.id} }"
          ><v-icon>mdi-pencil</v-icon></v-btn>
      </template>

    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import { IUserProfile } from '@/interfaces';
import { readAdminUsers } from '@/store/admin/getters';
import { dispatchGetUsers } from '@/store/admin/actions';

@Component
export default class AdminUsers extends Vue {
  public headers = [
    {
      text: 'Name',
      sortable: true,
      value: 'username',
      align: 'left',
    },
    {
      text: 'Email',
      sortable: true,
      value: 'email',
      align: 'left',
    },
    {
      text: 'Full Name',
      sortable: true,
      value: 'full_name',
      align: 'left',
    },
    {
      text: 'Is Disabled',
      sortable: true,
      value: 'disabled',
      align: 'left',
    },
    {
      text: 'Is Superuser',
      sortable: true,
      value: 'isSuperuser',
      align: 'left',
    },
    {
      text: 'Edit',
      value: 'id',
      align: 'left',
    }
  ];
  get users() {
    return readAdminUsers(this.$store);
  }

  public async mounted() {
    await dispatchGetUsers(this.$store);
  }
}
</script>
