package android.rapt.chat.sources

import androidx.room.*

/* Entities */
@Entity
data class DBContact(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "name") var name: String,
    @ColumnInfo(name = "phone") val phone: String,
    @ColumnInfo(name = "contact_id") var contactId: String,
    @ColumnInfo(name = "user_id") var userId: String,
    @ColumnInfo(name = "is_active") var isActive: Boolean
)

@Dao
interface ContactDao{

    @Query("SELECT * FROM dbcontact")
    suspend fun getAll(): List<DBContact>

    @Query("SELECT * FROM dbcontact WHERE phone = :phone")
    suspend fun getByPhone(phone: String): List<DBContact>

    @Query("SELECT * FROM dbcontact WHERE contact_id = :contactId")
    suspend fun getByContactId(contactId: String): List<DBContact>

    @Query("SELECT * FROM dbcontact WHERE " +
            "name LIKE '%' || :query || '%' "+
            "OR phone LIKE '%' || :query || '%'"
    )
    suspend fun search(query: String): List<DBContact>

    @Insert
    suspend fun insert(contact: DBContact)

    @Update
    suspend fun update(contact: DBContact)

    @Delete
    suspend fun delete(contact: DBContact)
}


@Database(entities = [DBContact::class], version = 1)
abstract class RaptDatabase : RoomDatabase() {
    abstract fun contactDao(): ContactDao
}