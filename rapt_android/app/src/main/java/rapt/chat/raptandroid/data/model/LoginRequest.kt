package rapt.chat.raptandroid.data.model

data class LoginRequest(
    val phone: String,
    val clientId: String,
    val clientSecret: String
)
