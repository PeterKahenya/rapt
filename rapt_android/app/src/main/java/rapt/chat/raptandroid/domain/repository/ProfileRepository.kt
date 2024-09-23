package rapt.chat.raptandroid.domain.repository

import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest

interface ProfileRepository {
    suspend fun getProfile(accessToken: String): ProfileResponse
    suspend fun updateProfile(accessToken: String, profileUpdateRequest: ProfileUpdateRequest): ProfileResponse
}