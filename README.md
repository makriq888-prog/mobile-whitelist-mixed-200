# short-key-list

Публичный репозиторий для серверной проверки VLESS-ключей из нескольких публичных апстримов и публикации итогового короткого списка.

Репозиторий хранит:

- код проверки ключей через `xray` и реальный HTTP-запрос;
- конфиг деплоя для `systemd`;
- публикуемый итоговый файл `data/short-key-list.txt`.

Секреты и серверное состояние не коммитятся:

- `.env` хранится только на сервере;
- `state/key-ratings.json` остается локальным;
- push-доступ к GitHub должен жить вне репозитория через `gh auth`, `.netrc` или другой системный credential helper.

## Что делает пайплайн

- собирает единый пул ключей из трех публичных источников;
- удаляет дубликаты;
- поднимает временный outbound через `xray` для каждого кандидата;
- проверяет прохождение реального запроса к `https://www.gstatic.com/generate_204`;
- ведет рейтинг стабильности ключей между циклами;
- публикует итоговый список в `data/short-key-list.txt`.

## Структура

- `scripts/check_key_list.py` — основной валидатор.
- `scripts/run_pipeline.py` — единая точка входа для проверки и публикации.
- `scripts/publish_key_list.py` — публикация результата в целевой git-репозиторий.
- `deploy/systemd/short-key-list.service` — unit для запуска пайплайна.
- `deploy/systemd/short-key-list.timer` — таймер для периодического запуска.
- `data/short-key-list.txt` — публикуемый итоговый список.
- `artifacts/short-key-list.txt` — локальный артефакт после проверки.
- `artifacts/check-report.json` — локальный отчет по последнему прогону.
- `state/key-ratings.json` — локальная история рейтингов на сервере.

## Источники по умолчанию

- `https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt`
- `https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt`
- `https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt`

## Локальный запуск

```bash
cp .env.example .env
python3 scripts/run_pipeline.py
```

Для ручной публикации после проверки:

```bash
python3 scripts/publish_key_list.py \
  --source artifacts/short-key-list.txt \
  --target-repo . \
  --target-file data/short-key-list.txt \
  --push
```

## Развертывание на сервере

Рекомендуемая схема после объединения: один git-клон публичного репозитория, без отдельного постоянного publish-клона.

1. Установить `python3`, `curl`, `git`, `xray`.
2. Склонировать публичный репозиторий.
3. Создать `.env` из `.env.example`.
4. Настроить системный доступ на push без хранения токена в репозитории.
5. Установить unit-файлы из `deploy/systemd/`.
6. Включить таймер:

```bash
systemctl daemon-reload
systemctl enable --now short-key-list.timer
```
