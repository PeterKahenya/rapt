package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class LoginResponse(
    @SerializedName("message")
    val message: String,
    @SerializedName("phone")
    val phone: String,
    @SerializedName("success")
    val success: Boolean
)

data class VerifyResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("expires_in")
    val expiresIn: Int
)

data class RefreshResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("expires_in")
    val expiresIn: Int
)

data class Auth(
    val accessToken: String,
    val phone: String,
    val userId: String,
    val expiresAt: Long
){
    fun isExpired(): Boolean {
        return System.currentTimeMillis() > expiresAt
    }
}




