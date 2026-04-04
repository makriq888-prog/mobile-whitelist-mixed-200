# short-key-list

Репозиторий публикует `200` VLESS-ключей, которые прошли проверку на момент последнего цикла.

Итоговый файл:

- `data/short-key-list.txt`

## Как собирается список

Каждый цикл:

1. загружает ключи из публичных источников;
2. удаляет дубликаты;
3. поднимает для каждого кандидата временный `xray` outbound;
4. проверяет прохождение запроса к `https://www.gstatic.com/generate_204`;
5. сохраняет историю результатов;
6. выбирает `200` ключей из успешно прошедших проверку.

При отборе учитывается рейтинг ключа по предыдущим циклам. Ключи с более стабильной историей попадают в итоговый список чаще.

## Что это значит на практике

- список не является зеркалом апстримов;
- в него не попадают дубликаты;
- в него не попадают ключи, которые не прошли текущую проверку;
- публикация не гарантирует, что ключ продолжит работать позже.

## Источники

- `https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt`
- `https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt`
- `https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt`

## Структура

- `data/short-key-list.txt` — публикуемый список.
- `scripts/check_key_list.py` — проверка и отбор.
- `scripts/run_pipeline.py` — запуск полного цикла.
- `scripts/publish_key_list.py` — публикация обновленного файла.

## Локальный запуск

```bash
cp .env.example .env
python3 scripts/run_pipeline.py
```
