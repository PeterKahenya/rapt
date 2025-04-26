package android.rapt.chat.models

import com.google.gson.annotations.SerializedName

data class Contact(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("contact_id")
    val contactId: String,
    @SerializedName("is_active")
    val isActive: Boolean,
    val phone: String,
    val name: String,
)

data class ContactUpload(
    val phone: String,
    val name: String
)

data class ContactUpdate(
    val name: String,
    val contactId: String
)

data class PhoneContact(
    val id: String,
    val name: String,
    val phone: String
)