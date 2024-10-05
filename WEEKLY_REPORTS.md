## Projektbeschreibung

1. **Kameraerkennung (Client-Frontend):**
                    ```
                    Das Frontend nutzt das SSDP M-Search-Protokoll, um nach dem Sony Kamera im selben Netzwerk zu suchen.
                    Nach erfolgreicher Erkennung wird eine Gerätebeschreibung (Divice discription ) von der Kamera abgerufen. Diese Beschreibung enthält wichtige Informationen wie das Modell und die ActionList-URL, die für die spätere Steuerung der Kamera verwendet wird.
                    ```

2. **Gerätebeschreibung an den Server senden (Frontend):**
                    ```
                    Die vom Frontend abgerufene Gerätebeschreibung wird an den Server gesendet.
                    Der Server extrahiert die relevanten Daten (z.B. Kameramodell, UUID) und speichert diese in den entsprechenden Datenbanken.
                    ```

3. **Modi und Funktionen abrufen (Backend):**
                    ```
                    Basierend auf dem Kameramodell prüft der Server, welche Betriebsmodi (z.B. Fotomodus, Videomodus) und API-Funktionen für das Modell (geteilt durch Modi) verfügbar sind.
                    Diese Informationen werden an das Frontend zurückgesendet.
                    ```

4. **Modus- und Funktionsauswahl (Frontend):**
                    ```
                    Der Benutzer kann aus den verfügbaren Modi (z.B. ShootMode, VideoMode) wählen und spezifische Funktionen (z.B. Foto aufnehmen, Video starten) auswählen.
                    Das Frontend sendet die ausgewählten Aktionen an den Server.
                    ```

5. **API-Anfragen und Camera-Steuerung (Backend):**
                    ```
                    Der Server generiert die entsprechenden JSON-RPC-Anfragen, die zum Steuern der Kamera verwendet werden.
                    Das Frontend sendet diese JSON-RPC-Anfragen direkt an die Kamera über die zuvor erhaltene ActionList-URL.
                    Die Kamera wird basierend auf den Benutzereingaben gesteuert.
                    ```

## Schlüsselkomponenten

1. **Frontend:** 
                    ```
                    Führt die Kamerasuche durch, zeigt dem Benutzer verfügbare Modi und Funktionen an, interagiert mit dem Benutzer, und steuert die Kamera basierend auf den gewählten API-Befehlen.
                    ```
2. **Backend:** 
                    ```
                    Verarbeitet die Kameradaten, verwaltet die verfügbaren Modi und APIs für verschiedene Kameramodelle und generiert die entsprechenden JSON-RPC-Anfragen zur Steuerung der Kamera.
                    ```

3. **Datenbank:** 
                    ```
                    Speichert Informationen zu den verschiedenen Kameramodellen, ihren Modi und den zugehörigen API-Funktionen.
                    ```

## Wöchentliche Reports

1. **5/10/2024: Aktuelle Projektstruktur**
                    ```
                    Das Projekt verwendet derzeit ausschließlich Python Django, ein high-level Python-Webframework. Im Projektordner finden Sie zwei Hauptordner (in Python Django als "Apps" genannt): Camera und Sony_camera_control.

                    Django generiert den Ordner Sony_camera_control (App) automatisch beim Erstellen des Projekts. Dies ist im Wesentlichen die Haupt-App des Projekts, die andere hinzugefügte Apps (wie unseren Camera-Ordner) verwaltet und steuert, wie diese miteinander und/oder mit dem Frontend kommunizieren. In Django übernimmt jede App eine separate Funktion. Beispielsweise könnte später eine App die Logik zur Abfrage, Extraktion von Kameradaten aus dem Frontend sowie das Abfragen der Datenbank für passende APIs übernehmen. Eine andere App könnte die Verwaltung der Datenbanken übernehmen und es dem Admin ermöglichen, deren Inhalt zu ändern.

                    Momentan dient die Camera App nur als Platzhalter, um die Kameraverbindungen zu testen und einige API-Aufrufe auszuprobieren. In der Camera App sind folgende Dateien wichtig:
                                        - admin.py: Hier werden die Modelle in die Admin-Benutzeroberfläche registriert.
                                        - models.py: Hier werden die Tabellenstrukturen in der Datenbank definiert.
                                        - urls.py: Verwaltet die Endpunkte zu den Funktionen (Views), die mit dem Frontend interagieren.
                                        - views.py: Hier werden diese Funktionen implementiert.

                    In "views.py" kann momentan nur nach der Kamera über SSDP M-Search gesucht, die Location-URL empfangen und die Gerätespezifikation der Kamera abgerufen werden. Die extrahierten Informationen werden dann in der Datenbank gespeichert. (Diese Funktionen können über das Frontend beim Start der App getestet werden.) Außerdem gibt es am Ende eine Funktion, um eine API-Anfrage an die Kamera zu senden.
                    ```

