package android.rapt.chat.sources

import android.rapt.chat.models.ChatRoom
import android.rapt.chat.models.ChatRoomCreate
import android.rapt.chat.models.ChatRoomUpdate
import retrofit2.http.*
import android.rapt.chat.models.Contact
import android.rapt.chat.models.ContactUpdate
import android.rapt.chat.models.ContactUpload
import android.rapt.chat.models.LoginResponse
import android.rapt.chat.models.ProfileUpdateRequest
import android.rapt.chat.models.RefreshResponse
import android.rapt.chat.models.User
import android.rapt.chat.models.VerifyResponse

interface RaptAPI {
    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @FieldMap fields: Map<String, String>
    ): LoginResponse

    @FormUrlEncoded
    @POST("auth/verify")
    suspend fun verify(
        @FieldMap fields: Map<String, String>
    ): VerifyResponse

    @FormUrlEncoded
    @POST("auth/refresh")
    suspend fun refresh(
        @FieldMap fields: Map<String, String>
    ): RefreshResponse

    @GET("auth/me")
    suspend fun getProfile(
        @Header("Authorization") accessToken: String
    ): User

    @PUT("auth/users/{userId}")
    suspend fun updateProfile(
        @Path("userId") userId: String,
        @Header("Authorization") accessToken: String,
        @Body profileUpdateRequest: ProfileUpdateRequest
    ): User

    @GET("auth/users/{userId}/contacts")
    suspend fun getContacts(
        @Header("Authorization") accessToken: String,
        @Path("userId") userId: String
    ): List<Contact>

    @POST("auth/users/{userId}/contacts")
    suspend fun addContacts(
        @Header("Authorization") accessToken: String,
        @Path("userId") userId: String,
        @Body addContactsRequest: List<ContactUpload>
    ): List<Contact>

    @PUT("auth/users/{userId}/contacts")
    suspend fun updateContact(
        @Header("Authorization") accessToken: String,
        @Path("userId") userId: String,
        @Body updateContactsRequest: List<ContactUpdate>
    ): List<Contact>

    // get chat rooms
    @GET("chat/rooms")
    suspend fun getChatRooms(@Header("Authorization") accessToken: String): List<ChatRoom>

    // create chat room
    @POST("chat/rooms")
    suspend fun createChatRoom(
        @Header("Authorization") accessToken: String,
        @Body chatRoomRequest: ChatRoomCreate
    ): ChatRoom

    // get chat room
    @GET("chat/rooms/{roomId}")
    suspend fun getChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String
    ): ChatRoom

    // update chat room
    @PUT("chat/rooms/{roomId}")
    suspend fun updateChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String,
        @Body chatRoomRequest: ChatRoomUpdate
    ): ChatRoom

    // delete chat room
    @DELETE("chat/rooms/{roomId}")
    suspend fun deleteChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String
    ): Nothing
}