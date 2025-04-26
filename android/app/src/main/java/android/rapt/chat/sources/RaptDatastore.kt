package android.rapt.chat.sources

import android.content.Context
import android.rapt.chat.models.Auth
import android.rapt.chat.dataStore
import android.util.Log
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.map

interface RaptDatastore {
    suspend fun saveAuth(auth: Auth)
    suspend fun getAuth(): Auth?
}

class RaptDataStoreImpl(private val context: Context) : RaptDatastore {

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
            val auth: Auth? = context.dataStore.data.map { preferences ->
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
            return auth
        } catch (e: Exception) {
            Log.e("RaptDataStoreImpl getAuth","$e")
            return null
        }
    }

}