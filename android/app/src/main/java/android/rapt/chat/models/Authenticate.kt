package android.rapt.chat.data.models

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val phone: String,
    val clientId: String,
    val clientSecret: String
)

fun LoginRequest.toFieldMap(): Map<String, String> {
    return mapOf(
        "phone" to phone,
        "client_id" to clientId,
        "client_secret" to clientSecret
    )
}

data class LoginResponse(
    val message: String,
    val phone: String,
    val success: Boolean
)

data class VerifyRequest(
    val phoneVerificationCode: String,
    val phone: String,
    val clientId: String,
    val clientSecret: String
)

fun VerifyRequest.toFieldMap(): Map<String, String> {
    return mapOf(
        "phone_verification_code" to phoneVerificationCode,
        "phone" to phone,
        "client_id" to clientId,
        "client_secret" to clientSecret
    )
}

data class VerifyResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("expires_in")
    val expiresIn: Int
)

data class RefreshRequest(
    val accessToken: String,
    val clientId: String,
    val clientSecret: String
)

fun RefreshRequest.toFieldMap(): Map<String, String> {
    return mapOf(
        "access_token" to accessToken,
        "client_id" to clientId,
        "client_secret" to clientSecret
    )
}

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