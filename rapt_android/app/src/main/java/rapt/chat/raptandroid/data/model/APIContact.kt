package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class APIContact(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("contact_id")
    val contactId: String,
    @SerializedName("is_active")
    val isActive: Boolean,
    val phone: String,
    val name: String,
)
