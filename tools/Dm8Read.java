import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;

/**
 * Local, read-only DM8 inspection helper.
 *
 * Connection settings are deliberately supplied through environment variables:
 * DM8_HOST, DM8_PORT, DM8_USER and DM8_PASSWORD.  This keeps credentials out
 * of the repository.  Only one SELECT statement is accepted.
 */
public final class Dm8Read {
    private Dm8Read() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !args[0].trim().matches("(?is)^select\\b.*")) {
            throw new IllegalArgumentException("Only one SELECT statement is allowed.");
        }

        String host = required("DM8_HOST");
        String port = required("DM8_PORT");
        String user = required("DM8_USER");
        String password = required("DM8_PASSWORD");
        String url = "jdbc:dm://" + host + ":" + port;

        Class.forName("dm.jdbc.driver.DmDriver");
        try (Connection connection = DriverManager.getConnection(url, user, password);
             PreparedStatement statement = connection.prepareStatement(args[0]);
             ResultSet result = statement.executeQuery()) {
            ResultSetMetaData meta = result.getMetaData();
            int count = meta.getColumnCount();
            for (int index = 1; index <= count; index++) {
                if (index > 1) System.out.print("\t");
                System.out.print(meta.getColumnLabel(index));
            }
            System.out.println();
            while (result.next()) {
                for (int index = 1; index <= count; index++) {
                    if (index > 1) System.out.print("\t");
                    String value = result.getString(index);
                    System.out.print(value == null ? "NULL" : value.replace("\n", "\\n"));
                }
                System.out.println();
            }
        }
    }

    private static String required(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Missing environment variable: " + name);
        }
        return value;
    }
}
