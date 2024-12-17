<script setup>
import { ref } from 'vue';
import { useDataStore } from '../DataStore';
import { Jimin } from '../Jimin.js';

const store = useDataStore();

// email and password
const email = ref('');
const password = ref('');

// count down
const count_down = ref(5);
let interval = null;

async function onClickLogin() {
  // send 
  let data = await Jimin.login(email.value, password.value);

  // update username
  store.user = data.user;

  // welcome message
  count_down.value = 5;

  interval = setInterval(() => {
    count_down.value -= 1;
    if (count_down.value == 0) {
      // clear interval
      clearInterval(interval);

      // redirect to dashboard
      store.changeView('dashboard');
    }
  }, 1000);
}

</script>

<template>
  <div class="flex flex-col h-full items-center justify-center">
    <div style="width: 400px; margin: 10rem auto;">

      <Card>
          <template #title>
            User Login
          </template>
          <template #content>
              <div v-if="store.user == null"
                class="login-info">
                <label for="">Email:</label>
                <InputText v-model="email" type="text" placeholder="Email" />

                <label for="">Password:</label>
                <InputText v-model="password" type="password" placeholder="Password" />

                <Button class="w-64" type="submit" label="Login" @click="onClickLogin" />
              </div>
              <div v-else>
                <p class="text-lg">
                  Welcome, {{ store.user.name }}
                </p>
                <p>
                  Redirecting to dashboard ... If not, you can click <br>
                  <Button @click="store.gotoMain('dashboard')">
                    <i class="fa fa-dashboard"></i>
                    Dashboard
                  </Button>
                </p>
              </div>
          </template>
      </Card>



    </div>
  </div>
</template>

<style scoped>
.login-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>