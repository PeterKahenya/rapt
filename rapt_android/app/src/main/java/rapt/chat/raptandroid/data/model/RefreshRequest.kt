package rapt.chat.raptandroid.data.model

import retrofit2.http.Field

data class RefreshRequest(
    @Field("access_token")
    val accessToken: String,
    @Field("client_id")
    val clientId: String,
    @Field("client_secret")
    val clientSecret: String
)
