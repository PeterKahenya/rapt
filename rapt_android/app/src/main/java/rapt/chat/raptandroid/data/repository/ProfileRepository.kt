package rapt.chat.raptandroid.data.repository

import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest

interface ProfileRepository {
    suspend fun getProfile(): ProfileResponse
    suspend fun updateProfile(userId: String, profileUpdateRequest: ProfileUpdateRequest): ProfileResponse
}
