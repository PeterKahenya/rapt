package rapt.chat.raptandroid.data.model

import retrofit2.http.Field

data class VerifyRequest(
    @Field("phone_verification_code") val phoneVerificationCode: String,
    @Field("phone") val phone: String,
    @Field("client_id") val clientId: String,
    @Field("client_secret") val clientSecret: String
)
