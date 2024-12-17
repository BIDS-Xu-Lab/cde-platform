<script setup>
import { RouterLink, useRouter } from 'vue-router';
// import createKindeClient from "@kinde-oss/kinde-auth-pkce-js";
const router = useRouter();
// (async () => {
//   const kinde = await createKindeClient({
//     client_id: import.meta.env.VITE_KINDE_CLIENT_ID,
//     domain: import.meta.env.VITE_KINDE_AUTH_DOMAIN,
//     redirect_uri: window.location.origin + '/login_callback'
//   });
// };

// let kinde = null;

// createKindeClient({
//     client_id: import.meta.env.VITE_KINDE_CLIENT_ID,
//     domain: import.meta.env.VITE_KINDE_AUTH_DOMAIN,
//     redirect_uri: window.location.origin + '/login_callback',
//     on_redirect_callback: (user, appState) => {
//         console.log({user, appState});s
//         if (user) {
//             // render logged in view
//         } else {
//             // render logged out view
//         }
//     }
// }).then((client) => {
//     kinde = client;
//     console.log('Kinde client created', kinde);
// });

async function onClickSignin() {
    console.log('* clicked Sign in', kinde);
    await router.push('/login');
};

async function onClickLogout() {
    // const kinde = await createKindeClient({
    //     client_id: import.meta.env.VITE_KINDE_CLIENT_ID,
    //     domain: import.meta.env.VITE_KINDE_AUTH_DOMAIN,
    //     redirect_uri: window.location.origin
    // });
    console.log('* clicked Logout');
    
}
</script>

<template>
<div id="homepage">
    <div style="font-size: 4rem;">
        <i class="fa fa-edit"></i>
        CDE Reviewer
    </div>
    <div style="font-size: 1rem; font-style: italic;">
        Create, share, and visualize Common Data Elements (CDEs) in a collaborative environment
    </div>
    <div id="logged_out_view">
        <button type="button" 
        @click="onClickSignin">Sign in</button>
        <button type="button">Register</button>
        <button type="button" @click="onClickLogout">Logout</button>
    </div>
    <div class="py-3">
        <RouterLink to="/main">
            Get Started!
        </RouterLink>
    </div>
</div>

</template>

<style scoped>
#homepage {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-size: 20px;
    font-weight: bold;
}
</style>