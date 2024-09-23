package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class VerifyResponse(
   @SerializedName("access_token")
   val accessToken: String,
   @SerializedName("token_type")
   val tokenType: String
)