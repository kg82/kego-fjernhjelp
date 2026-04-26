// KEGO Data — Kunder-panel for support-klienten
import 'dart:convert';
// common.dart definerer sin egen Dialog<T> — skjul Flutter-widgeten for å unngå konflikt
import 'package:flutter/material.dart' hide Dialog;
import 'package:flutter_hbb/common.dart';
import 'package:http/http.dart' as http;

const _peersUrl = 'https://remote.baksystem.no/peers?token=kego-peers-2026';

class _KegoPeer {
  final String id;
  final DateTime lastSeen;
  final String ip;
  _KegoPeer({required this.id, required this.lastSeen, required this.ip});

  // Antall minutter siden sist sett
  int get minutesAgo =>
      DateTime.now().difference(lastSeen).inMinutes;

  // Online-indikator basert på sist registrert med hbbs
  Color get statusColor {
    if (minutesAgo < 30) return Colors.green.shade600;
    if (minutesAgo < 360) return Colors.orange.shade600;
    return Colors.grey.shade500;
  }

  String get statusText {
    if (minutesAgo < 2) return 'Nylig tilkoblet';
    if (minutesAgo < 60) return '$minutesAgo min siden';
    final h = lastSeen.hour.toString().padLeft(2, '0');
    final m = lastSeen.minute.toString().padLeft(2, '0');
    return '${lastSeen.day}.${lastSeen.month} $h:$m';
  }
}

class KegoCustomersButton extends StatelessWidget {
  const KegoCustomersButton({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 28,
      child: OutlinedButton.icon(
        icon: const Icon(Icons.people_alt_outlined, size: 14),
        label: const Text('Kunder', style: TextStyle(fontSize: 12)),
        style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 10)),
        onPressed: () => showDialog(
          context: context,
          builder: (_) => const _KegoCustomersDialog(),
        ),
      ),
    );
  }
}

class _KegoCustomersDialog extends StatefulWidget {
  const _KegoCustomersDialog({Key? key}) : super(key: key);

  @override
  State<_KegoCustomersDialog> createState() => _KegoCustomersDialogState();
}

class _KegoCustomersDialogState extends State<_KegoCustomersDialog> {
  List<_KegoPeer> _peers = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final resp = await http
          .get(Uri.parse(_peersUrl))
          .timeout(const Duration(seconds: 8));
      if (resp.statusCode != 200) throw Exception('HTTP ${resp.statusCode}');
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      final list = (data['peers'] as List).map((p) {
        DateTime dt;
        try {
          dt = DateTime.parse((p['last_seen'] as String).replaceFirst(' ', 'T'));
        } catch (_) {
          dt = DateTime(2000);
        }
        return _KegoPeer(
          id: p['id'] as String,
          lastSeen: dt,
          ip: (p['ip'] as String? ?? '').replaceAll('::ffff:', ''),
        );
      }).toList();

      // Sort: most recently seen first
      list.sort((a, b) => b.lastSeen.compareTo(a.lastSeen));

      if (mounted) setState(() { _peers = list; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480, maxHeight: 540),
        child: Material(
          color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
          child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            Container(
              decoration: const BoxDecoration(
                  color: Color(0xFF1a1a2e),
                  borderRadius:
                      BorderRadius.vertical(top: Radius.circular(12))),
              padding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(children: [
                const Icon(Icons.people_alt_outlined,
                    color: Colors.white, size: 18),
                const SizedBox(width: 8),
                const Expanded(
                    child: Text('Kunder',
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 15))),
                IconButton(
                    icon: const Icon(Icons.refresh,
                        color: Colors.white70, size: 18),
                    tooltip: 'Oppdater',
                    onPressed: _load,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints()),
                const SizedBox(width: 8),
                IconButton(
                    icon: const Icon(Icons.close,
                        color: Colors.white70, size: 18),
                    onPressed: () => Navigator.of(context).pop(),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints()),
              ]),
            ),
            // Body
            Flexible(
              child: _loading
                  ? const Padding(
                      padding: EdgeInsets.all(32),
                      child: CircularProgressIndicator())
                  : _error != null
                      ? Padding(
                          padding: const EdgeInsets.all(24),
                          child: Text('Feil: $_error',
                              style: const TextStyle(color: Colors.red)))
                      : _peers.isEmpty
                          ? const Padding(
                              padding: EdgeInsets.all(24),
                              child: Text('Ingen registrerte kunder'))
                          : ListView.separated(
                              padding:
                                  const EdgeInsets.symmetric(vertical: 6),
                              itemCount: _peers.length,
                              separatorBuilder: (_, __) =>
                                  const Divider(height: 1, indent: 48),
                              itemBuilder: (_, i) {
                                final p = _peers[i];
                                return ListTile(
                                  dense: true,
                                  leading: CircleAvatar(
                                    radius: 16,
                                    backgroundColor: p.statusColor,
                                    child: const Icon(Icons.computer,
                                        color: Colors.white, size: 16),
                                  ),
                                  title: Text(p.id,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.w600,
                                          fontSize: 14)),
                                  subtitle: Text(
                                      '${p.ip.isNotEmpty ? "${p.ip}  ·  " : ""}${p.statusText}',
                                      style: TextStyle(
                                          fontSize: 11,
                                          color: isDark
                                              ? Colors.white54
                                              : Colors.black45)),
                                  trailing: TextButton(
                                    style: TextButton.styleFrom(
                                        padding:
                                            const EdgeInsets.symmetric(
                                                horizontal: 12,
                                                vertical: 4),
                                        backgroundColor:
                                            p.minutesAgo < 30
                                                ? Colors.green.shade700
                                                : Colors.blueGrey
                                                    .shade700,
                                        foregroundColor: Colors.white,
                                        shape: RoundedRectangleBorder(
                                            borderRadius:
                                                BorderRadius.circular(6))),
                                    onPressed: () {
                                      Navigator.of(context).pop();
                                      connect(context, p.id);
                                    },
                                    child: const Text('Koble til',
                                        style: TextStyle(fontSize: 12)),
                                  ),
                                );
                              }),
            ),
          ],
        ),
      ),
    ),
  );
  }
}
