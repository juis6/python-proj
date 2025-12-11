import java.awt.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableRowSorter;

public class PlantGuide extends JFrame {

    private JTable table;
    private DefaultTableModel tableModel;
    private JTextArea detailsArea;
    private JLabel statsLabel;
    private List<PlantData> plants = new ArrayList<>();

    static class PlantData {
        String scientificName;
        String commonName;
        String family;
        String severity;
        String pid;
        String wikipediaUrl;
        List<String> allCommonNames = new ArrayList<>();
        List<String> symptoms = new ArrayList<>();
        List<String> animals = new ArrayList<>();
    }

    public PlantGuide(String dataFilePath) {
        setTitle("🌿 GreenLeaf Guide - Енциклопедія отруйних рослин");
        setSize(1400, 800);
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        setLocationRelativeTo(null);

        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        setJMenuBar(createMenuBar());

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(15, 15, 15, 15));
        mainPanel.setBackground(new Color(245, 255, 250));
        setContentPane(mainPanel);

        JPanel topPanel = new JPanel(new BorderLayout());
        topPanel.setBackground(new Color(34, 139, 34));
        topPanel.setBorder(BorderFactory.createEmptyBorder(15, 20, 15, 20));

        JLabel headerLabel = new JLabel("🌿 Енциклопедія отруйних рослин");
        headerLabel.setFont(new Font("Segoe UI", Font.BOLD, 26));
        headerLabel.setForeground(Color.WHITE);
        topPanel.add(headerLabel, BorderLayout.WEST);

        statsLabel = new JLabel("Завантаження...");
        statsLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        statsLabel.setForeground(new Color(200, 255, 200));
        topPanel.add(statsLabel, BorderLayout.EAST);

        mainPanel.add(topPanel, BorderLayout.NORTH);

        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
        splitPane.setDividerLocation(850);
        splitPane.setResizeWeight(0.6);

        JPanel leftPanel = new JPanel(new BorderLayout(5, 5));
        leftPanel.setBackground(Color.WHITE);

        JLabel tableTitle = new JLabel("Список рослин (клікни для деталей)");
        tableTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        tableTitle.setBorder(new EmptyBorder(5, 10, 5, 10));
        leftPanel.add(tableTitle, BorderLayout.NORTH);

        String[] columns = {"Наукова назва", "Поширена назва", "Родина", "Небезпека"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) { return false; }
            @Override
            public Class<?> getColumnClass(int column) { return String.class; }
        };

        table = new JTable(tableModel);
        table.setRowHeight(28);
        table.setFont(new Font("SansSerif", Font.PLAIN, 13));
        table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        table.getTableHeader().setBackground(new Color(46, 125, 50));
        table.getTableHeader().setForeground(Color.WHITE);
        table.getTableHeader().setFont(new Font("SansSerif", Font.BOLD, 14));
        
        TableRowSorter<DefaultTableModel> sorter = new TableRowSorter<>(tableModel);
        table.setRowSorter(sorter);

        table.getColumnModel().getColumn(3).setCellRenderer(new DefaultTableCellRenderer() {
            @Override
            public Component getTableCellRendererComponent(JTable table, Object value,
                    boolean isSelected, boolean hasFocus, int row, int column) {
                Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
                if (column == 3 && value != null) {
                    String severity = value.toString().toLowerCase();
                    if (!isSelected) {
                        if (severity.contains("severe") || severity.contains("critical") || severity.contains("high")) {
                            c.setBackground(new Color(255, 200, 200));
                            c.setForeground(new Color(139, 0, 0));
                        } else if (severity.contains("moderate") || severity.contains("medium")) {
                            c.setBackground(new Color(255, 245, 200));
                            c.setForeground(new Color(139, 69, 0));
                        } else if (severity.contains("low") || severity.contains("mild")) {
                            c.setBackground(new Color(200, 255, 200));
                            c.setForeground(new Color(0, 100, 0));
                        } else {
                            c.setBackground(Color.WHITE);
                            c.setForeground(Color.BLACK);
                        }
                    }
                } else if (!isSelected) {
                    c.setBackground(Color.WHITE);
                    c.setForeground(Color.BLACK);
                }
                return c;
            }
        });

        table.getSelectionModel().addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting() && table.getSelectedRow() >= 0) {
                showPlantDetails(table.convertRowIndexToModel(table.getSelectedRow()));
            }
        });

        leftPanel.add(new JScrollPane(table), BorderLayout.CENTER);

        JPanel rightPanel = new JPanel(new BorderLayout(5, 5));
        rightPanel.setBackground(new Color(250, 250, 255));

        JLabel detailsTitle = new JLabel("Деталі / Результати аналітики");
        detailsTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        detailsTitle.setBorder(new EmptyBorder(5, 10, 5, 10));
        rightPanel.add(detailsTitle, BorderLayout.NORTH);

        detailsArea = new JTextArea();
        detailsArea.setEditable(false);
        detailsArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        detailsArea.setLineWrap(true);
        detailsArea.setWrapStyleWord(true);
        detailsArea.setMargin(new Insets(10, 10, 10, 10));
        detailsArea.setText("1. Оберіть рослину в таблиці зліва.\nАБО\n2. Використайте меню 'Аналітика' зверху для запуску Python-скриптів.");
        
        rightPanel.add(new JScrollPane(detailsArea), BorderLayout.CENTER);

        splitPane.setLeftComponent(leftPanel);
        splitPane.setRightComponent(rightPanel);
        mainPanel.add(splitPane, BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setBackground(new Color(240, 240, 240));
        bottomPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        bottomPanel.add(new JLabel("📁 Джерело: " + new File(dataFilePath).getName()), BorderLayout.WEST);
        JLabel warning = new JLabel("⚠️ Інформація про токсичність тільки для ознайомлення");
        warning.setForeground(new Color(204, 0, 0));
        bottomPanel.add(warning, BorderLayout.EAST);
        mainPanel.add(bottomPanel, BorderLayout.SOUTH);

        loadPlants(dataFilePath);
    }

    private JMenuBar createMenuBar() {
        JMenuBar menuBar = new JMenuBar();
        
        JMenu analyticsMenu = new JMenu("Аналітика (Python)");
        analyticsMenu.setFont(new Font("Segoe UI", Font.BOLD, 13));

        JMenuItem topFamiliesItem = new JMenuItem("Топ родин рослин");
        topFamiliesItem.addActionListener(e -> runPythonScript("top_families.py", null));

        JMenuItem severityItem = new JMenuItem("Статистика небезпеки");
        severityItem.addActionListener(e -> runPythonScript("severity_stats.py", null));

        JMenuItem animalSearchItem = new JMenuItem("Пошук небезпечних для тварини...");
        animalSearchItem.addActionListener(e -> {
            String animal = JOptionPane.showInputDialog(this, 
                "Введіть назву тварини (наприклад: dogs, cats, horses):", 
                "Пошук загрози", JOptionPane.QUESTION_MESSAGE);
            if (animal != null && !animal.trim().isEmpty()) {
                runPythonScript("search_animals.py", animal.trim());
            }
        });

        analyticsMenu.add(topFamiliesItem);
        analyticsMenu.add(severityItem);
        analyticsMenu.addSeparator();
        analyticsMenu.add(animalSearchItem);

        menuBar.add(analyticsMenu);
        return menuBar;
    }

    private void runPythonScript(String scriptName, String arg) {
        new Thread(() -> {
            SwingUtilities.invokeLater(() -> {
                detailsArea.setText("Запуск скрипта: " + scriptName + "...\nЧекайте...");
                detailsArea.setForeground(new Color(0, 0, 139));
            });

            try {
                List<String> command = new ArrayList<>();
                command.add("python3");
                command.add("tasks/" + scriptName);
                if (arg != null) {
                    command.add(arg);
                }

                ProcessBuilder pb = new ProcessBuilder(command);
                pb.redirectErrorStream(true);
                
                Process process = pb.start();

                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8));
                
                StringBuilder output = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }
                
                int exitCode = process.waitFor();

                SwingUtilities.invokeLater(() -> {
                    detailsArea.setForeground(Color.BLACK);
                    if (exitCode == 0) {
                        detailsArea.setText(output.toString());
                    } else {
                        detailsArea.setText("Помилка виконання:\n" + output.toString());
                        if (output.toString().contains("ImportError")) {
                            detailsArea.append("\nПІДКАЗКА: Якщо помилка в 'from .utils', спробуйте змінити в Python файлі на 'from utils'");
                        }
                    }
                    detailsArea.setCaretPosition(0);
                });

            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> {
                    detailsArea.setText("Не вдалося запустити процес:\n" + e.getMessage());
                });
            }
        }).start();
    }
    private void loadPlants(String path) {
        File file = new File(path);
        if (!file.exists()) return;

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
            
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) sb.append(line).append("\n");

            List<String> jsonObjects = splitJsonObjects(sb.toString());
            for (String jsonObject : jsonObjects) {
                PlantData plant = parseObject(jsonObject);
                if (plant != null) {
                    plants.add(plant);
                    tableModel.addRow(new Object[]{plant.scientificName, plant.commonName, plant.family, plant.severity});
                }
            }
            updateStats();
        } catch (Exception e) { e.printStackTrace(); }
    }

    private void updateStats() {
        long highDanger = plants.stream()
            .filter(p -> p.severity.toLowerCase().contains("high") || p.severity.toLowerCase().contains("extreme") || p.severity.toLowerCase().contains("severe"))
            .count();
        statsLabel.setText(String.format("📊 Всього: %d рослин | ☠️ Високонебезпечних: %d", plants.size(), highDanger));
    }

    private void showPlantDetails(int index) {
        if (index < 0 || index >= plants.size()) return;
        
        PlantData plant = plants.get(index);
        StringBuilder details = new StringBuilder();
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("🌿 НАУКОВА НАЗВА\n");
        details.append("═══════════════════════════════════════════════════\n");
        details.append(plant.scientificName).append("\n\n");
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("💬 ПОШИРЕНІ НАЗВИ\n");
        details.append("═══════════════════════════════════════════════════\n");
        if (plant.allCommonNames.isEmpty()) {
            details.append("  (немає даних)\n");
        } else {
            for (String name : plant.allCommonNames) {
                details.append("  • ").append(name).append("\n");
            }
        }
        details.append("\n");
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("🏛️ РОДИНА\n");
        details.append("═══════════════════════════════════════════════════\n");
        details.append(plant.family).append("\n\n");
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("☠️ РІВЕНЬ НЕБЕЗПЕКИ\n");
        details.append("═══════════════════════════════════════════════════\n");
        details.append(plant.severity).append("\n\n");
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("🤢 СИМПТОМИ ОТРУЄННЯ\n");
        details.append("═══════════════════════════════════════════════════\n");
        if (plant.symptoms.isEmpty()) {
            details.append("  (немає даних)\n");
        } else {
            for (String symptom : plant.symptoms) {
                details.append("  ⚕️ ").append(symptom).append("\n");
            }
        }
        details.append("\n");
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("🐾 НЕБЕЗПЕКА ДЛЯ ТВАРИН\n");
        details.append("═══════════════════════════════════════════════════\n");
        if (plant.animals.isEmpty()) {
            details.append("  (немає даних)\n");
        } else {
            for (String animal : plant.animals) {
                details.append("  🐕 ").append(animal).append("\n");
            }
        }
        details.append("\n");
        
        details.append("═══════════════════════════════════════════════════\n");
        details.append("🔗 ДОДАТКОВА ІНФОРМАЦІЯ\n");
        details.append("═══════════════════════════════════════════════════\n");
        details.append("ID: ").append(plant.pid).append("\n");
        if (plant.wikipediaUrl != null && !plant.wikipediaUrl.isEmpty()) {
            details.append("Wikipedia: ").append(plant.wikipediaUrl).append("\n");
        }
        
        detailsArea.setText(details.toString());
        detailsArea.setCaretPosition(0);
    }

    private List<String> splitJsonObjects(String fullJson) {
        List<String> objects = new ArrayList<>();
        int braceCount = 0; int startIndex = -1; boolean inString = false;
        for (int i = 0; i < fullJson.length(); i++) {
            char c = fullJson.charAt(i);
            if (c == '"' && (i==0 || fullJson.charAt(i-1) != '\\')) inString = !inString;
            if (inString) continue;
            if (c == '{') { if (braceCount++ == 0) startIndex = i; }
            else if (c == '}') { if (--braceCount == 0 && startIndex != -1) { objects.add(fullJson.substring(startIndex, i + 1)); startIndex = -1; } }
        }
        return objects;
    }

    private PlantData parseObject(String json) {
        PlantData p = new PlantData();
        p.scientificName = extractValue(json, "\"name\":\\s*\"([^\"]+)\",\\s*\"pid\"");
        p.pid = extractValue(json, "\"pid\":\\s*\"([^\"]+)\"");
        p.family = extractValue(json, "\"family\":\\s*\"([^\"]+)\"");
        p.wikipediaUrl = extractValue(json, "\"wikipedia_url\":\\s*\"([^\"]+)\"");
        String sev = extractValue(json, "\"severity\":\\s*\\{[^}]*\"label\":\\s*\"([^\"]+)\"");
        p.severity = sev != null ? sev : "Unknown";
        p.allCommonNames = extractList(json, "\"common\":\\s*\\[(.*?)\\]", "\"name\":\\s*\"([^\"]+)\"");
        p.commonName = p.allCommonNames.isEmpty() ? "-" : p.allCommonNames.get(0);
        p.symptoms = extractList(json, "\"symptoms\":\\s*\\[(.*?)\\]", "\"name\":\\s*\"([^\"]+)\"");
        p.animals = extractSimpleList(json, "\"animals\":\\s*\\[(.*?)\\]");
        return p.scientificName != null ? p : null;
    }

    private String extractValue(String src, String pat) { Matcher m = Pattern.compile(pat, Pattern.DOTALL).matcher(src); return m.find() ? m.group(1) : null; }
    
    private List<String> extractList(String src, String blk, String itm) {
        List<String> r = new ArrayList<>(); Matcher bm = Pattern.compile(blk, Pattern.DOTALL).matcher(src);
        if (bm.find()) { Matcher im = Pattern.compile(itm).matcher(bm.group(1)); while(im.find()) r.add(im.group(1)); }
        return r;
    }
    
    private List<String> extractSimpleList(String src, String blk) {
        List<String> r = new ArrayList<>(); Matcher bm = Pattern.compile(blk, Pattern.DOTALL).matcher(src);
        if (bm.find()) { Matcher im = Pattern.compile("\"([^\"]+)\"").matcher(bm.group(1)); 
            while(im.find()) { String s = im.group(1); r.add(s.substring(0,1).toUpperCase() + s.substring(1)); } 
        } return r;
    }

    public static void main(String[] args) {
        String path = "plants.json";
        if (args.length > 0) path = args[0];
        final String fPath = path;
        SwingUtilities.invokeLater(() -> new PlantGuide(fPath).setVisible(true));
    }
}