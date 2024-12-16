<script setup>
import { $dt } from '@primevue/themes';
import { ref } from 'vue';
import { set } from 'vue-demi';

const email = ref('');
const password = ref('');

const username = ref('');

async function onClickLogin() {
  console.log('clicked Login', email.value, password.value);

  // sent email and password to server
  // server will return a token
  // store token in local storage
  let rsp = await fetch('http://localhost:8001/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email.value,
      password: password.value
    })
  });

  let data = await rsp.json();

  console.log('response', data);

  if (data.token) {
    localStorage.setItem('token', data.token);
    console.log('token stored');
  } else {
    console.log('no token');
  }

  // update username
  username.value = email.value;
}


</script>

<template>
  <div>
    <h1>Login</h1>

    <InputText v-model="email" type="text" placeholder="Email" />
    <InputText v-model="password" type="password" placeholder="Password" />

    <Button type="submit" label="Login" @click="onClickLogin" />

    Username: {{  username }}
  </div>
</template>

<style scoped>
</style>