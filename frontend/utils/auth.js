import { api } from './api'

export function getToken() {
  return uni.getStorageSync('token')
}

export function setToken(token) {
  uni.setStorageSync('token', token)
}

export function clearToken() {
  uni.removeStorageSync('token')
}

export async function silentLogin() {
  const [err, res] = await uni.login({ provider: 'weixin' })
  if (err) {
    console.error('wx.login failed', err)
    return null
  }
  try {
    const data = await api.login(res.code)
    setToken(data.token)
    return data
  } catch (e) {
    console.error('silentLogin failed', e)
    return null
  }
}
