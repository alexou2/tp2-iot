import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

app.mount('#app')

// import express from 'express'
// const server = express()
// const port = 8080

// server.get('/', (req, res) => {
//   res.send('Hello World!')
// })

// server.listen(port, () => {
//   console.log(`Example app listening on port ${port}`)
// })
