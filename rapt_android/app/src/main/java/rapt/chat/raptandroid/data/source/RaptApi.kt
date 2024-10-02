package rapt.chat.raptandroid.data.source.api

import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.model.ChatRoomCreateRequest
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.data.model.RefreshResponse
import rapt.chat.raptandroid.data.model.VerifyResponse
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface RaptApi {
    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @Field("phone") phone: String,
        @Field("client_id") clientId: String,
        @Field("client_secret") clientSecret: String
    ): LoginResponse

    @FormUrlEncoded
    @POST("auth/verify")
    suspend fun verify(
        @Field("phone_verification_code") phoneVerificationCode: String,
        @Field("phone") phone: String,
        @Field("client_id") clientId: String,
        @Field("client_secret") clientSecret: String
    ): VerifyResponse

    @FormUrlEncoded
    @POST("auth/refresh")
    suspend fun refresh(
        @Field("access_token")
        accessToken: String,
        @Field("client_id")
        clientId: String,
        @Field("client_secret")
        clientSecret: String
    ): RefreshResponse

    // get profile
    @GET("auth/me")
    suspend fun getProfile(@Header("Authorization") accessToken: String): ProfileResponse

    //update profile
    @PUT("auth/users/{userId}")
    suspend fun updateProfile(
        @Path("userId") userId: String,
        @Header("Authorization") accessToken: String,
        @Body profileUpdateRequest: ProfileUpdateRequest
    ): ProfileResponse

    // get chat rooms
    @GET("chat/rooms")
    suspend fun getChatRooms(@Header("Authorization") accessToken: String): List<ChatRoom>

    // get chat room
    @GET("chat/rooms/{roomId}")
    suspend fun getChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String
    ): ChatRoom

    // create chat room
    @POST("chat/rooms")
    suspend fun createChatRoom(
        @Header("Authorization") accessToken: String,
        @Body chatRoomRequest: ChatRoomCreateRequest
    ): ChatRoom

    // update chat room
    @PUT("chat/rooms/{roomId}")
    suspend fun updateChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String,
        @Body chatRoomRequest: ChatRoomCreateRequest
    ): ChatRoom

    // delete chat room
    @DELETE("chat/rooms/{roomId}")
    suspend fun deleteChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String
    ): Nothing


}