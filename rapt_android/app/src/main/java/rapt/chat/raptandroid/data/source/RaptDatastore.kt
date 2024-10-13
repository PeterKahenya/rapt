package rapt.chat.raptandroid.data.source

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.map
import rapt.chat.raptandroid.data.model.Auth
import rapt.chat.raptandroid.dataStore

interface RaptDataStore{
    suspend fun saveAuth(auth: Auth)
    suspend fun getAuth(): Auth?
}

class RaptDataStoreImpl(val context: Context): RaptDataStore {

    private val accessTokenKey = stringPreferencesKey("access_token")
    private val phoneKey = stringPreferencesKey("phone")
    private val userIdKey = stringPreferencesKey("user_id")
    private val expiresAtKey = longPreferencesKey("expires_at")


    override suspend fun saveAuth(auth: Auth) {
        context.dataStore.edit { settings ->
            settings[accessTokenKey] = auth.accessToken
            settings[phoneKey] = auth.phone
            settings[userIdKey] = auth.userId
            settings[expiresAtKey] = auth.expiresAt
        }
    }

    override suspend fun getAuth(): Auth? {
        try {
            val accessToken: Auth? = context.dataStore.data.map { preferences ->
//                println("getAuth: $preferences")
                if (
                    preferences[accessTokenKey] == null ||
                    preferences[phoneKey] == null ||
                    preferences[userIdKey] == null ||
                    preferences[expiresAtKey] == null
                ) {
                    null
                } else {
                    Auth(
                        preferences[accessTokenKey] ?: "",
                        preferences[phoneKey] ?: "",
                        preferences[userIdKey] ?: "",
                        preferences[expiresAtKey] ?: 0
                    )
                }
            }.firstOrNull()
            return accessToken
        } catch (e: Exception) {
            println("getAuth Error: $e")
            return null
        }
    }

}