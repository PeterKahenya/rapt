package rapt.chat.raptandroid.data.model

data class Sender(
    val client_apps: List<Any>,
    val contacts: List<Any>,
    val created_at: String,
    val id: String,
    val is_active: Boolean,
    val is_superuser: Boolean,
    val is_verified: Boolean,
    val last_seen: String,
    val name: String,
    val phone: String,
    val phone_verification_code: String,
    val phone_verification_code_expiry_at: String,
    val roles: List<Any>,
    val updated_at: String
)