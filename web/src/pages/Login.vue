<script setup>
import { ref } from 'vue';
import { useDataStore } from '../DataStore';
import { Jimin } from '../Jimin.js';

const store = useDataStore();

// email and password
const email = ref('');
const password = ref('');

// server message
const msg = ref('');

// count down
const count_down = ref(5);
let interval = null;

async function onClickLogin() {
  // login
  try {
    let data = await Jimin.login(email.value, password.value);
    // update username
    store.user = data.user;
    store.gotoMain('dashboard');

    // let store start refreshing token to remain session
    store.startRefreshToken();

  } catch (error) {
    console.log('error:', error);
    msg.value = 'Login failed. Please check your email and password.';
  }

}

</script>

<template>
  <div class="flex flex-col h-full items-center justify-center">
    <div style="width: 400px; margin: 10rem auto;">

      <Card>
          <template #title>
            <b>
              User Login
            </b>
          </template>
          <template #content>
              <div v-if="store.user == null"
                class="login-info">
                <div v-if="msg != ''">
                  <Message severity="warn">
                    {{ msg }}
                  </Message>
                </div>
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
                  Redirecting to dashboard ... <br>
                  If not, you can click 
                  <Button @click="store.gotoMain('dashboard')" variant="link">
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