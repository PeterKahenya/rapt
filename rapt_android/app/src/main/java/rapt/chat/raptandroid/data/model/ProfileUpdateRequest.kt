package rapt.chat.raptandroid.data.model

import retrofit2.http.Field

data class ProfileUpdateRequest(
    val name: String? = null,
    @Field("device_fcm_token")
    val deviceFcmToken: String? = null,
)
