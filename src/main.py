"""
Refinery HTML to Text Cleaner - Apify Actor
Ultra-fast HTML text extraction for RAG and AI agents
"""

import asyncio
import json
import time
import httpx
from apify import Actor

async def fetch_url(url: str) -> str:
    """Fetch HTML content from a URL"""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

async def main():
    async with Actor:
        # Get input from Apify
        input_data = await Actor.get_input() or {}
        
        # Get options
        include_metadata = input_data.get('includeMetadata', True)
        remove_scripts = input_data.get('removeScripts', True)
        remove_styles = input_data.get('removeStyles', True)
        extract_mentions = input_data.get('extractMentions', False)
        extract_hashtags = input_data.get('extractHashtags', False)
        
        # Get HTML content (either raw_payload or URLs)
        raw_payload = input_data.get('raw_payload', '')
        urls = input_data.get('urls', [])
        
        # URL mode when urls are set (Console prefills both url + sample HTML — urls win)
        if urls:
            Actor.log.info(f'Fetching {len(urls)} URLs')
            html_contents = []
            for url in urls:
                try:
                    html = await fetch_url(url)
                    html_contents.append(html)
                    Actor.log.info(f'Fetched {url} ({len(html)} bytes)')
                except Exception as e:
                    Actor.log.error(f'Failed to fetch {url}: {str(e)}')
            # Combine all HTML if multiple URLs
            html = '\n\n'.join(html_contents) if html_contents else ''
        else:
            html = raw_payload
        
        if not html or not str(html).strip():
            if urls:
                msg = (
                    'All URL fetches failed (site may block Apify IPs, e.g. Cloudflare). '
                    'Paste HTML from your browser or use an open URL like https://example.com'
                )
                Actor.log.error(msg)
                await Actor.push_data({
                    'success': False,
                    'error': msg,
                    'text': '',
                    'word_count': 0,
                    'content_type': 'web',
                })
                return
            Actor.log.error('No HTML provided in input')
            raise ValueError('No HTML provided in input')
        
        # Validate payload size (10MB limit)
        if len(html) > 10 * 1024 * 1024:
            Actor.log.error('Payload too large (max 10MB)')
            raise ValueError('Payload too large (max 10MB)')
        
        Actor.log.info(f'Processing HTML payload ({len(html)} bytes)')
        
        start_time = time.time()
        
        try:
            # Import refinery core
            import sys
            sys.path.append('/app/refinery_core_src')
            import refinery_core
            
            # Process HTML with Refinery
            result_json = refinery_core.refinery_json(html)
            
            Actor.log.info(f'Refinery returned: {type(result_json)}')
            
            # Handle if result is already a dict or needs parsing
            if isinstance(result_json, dict):
                result = result_json
            else:
                result = json.loads(result_json)
            
            # Add performance metrics
            processing_time = (time.time() - start_time) * 1000
            result['processing_time_ms'] = round(processing_time, 2)
            result['success'] = True
            
            # Apply options
            if not include_metadata:
                # Keep only essential fields
                result = {
                    'text': result.get('text', ''),
                    'success': result.get('success', True)
                }
            
            if not extract_mentions:
                result.pop('mentions', None)
            
            if not extract_hashtags:
                result.pop('hashtags', None)
            
            Actor.log.info(f'Extraction complete in {processing_time:.2f}ms')
            
            # Push output to Apify
            await Actor.push_data(result)
            
            Actor.log.info('Output pushed successfully')
            
        except Exception as e:
            Actor.log.error(f'Extraction failed: {str(e)}')
            Actor.log.error(f'Exception type: {type(e).__name__}')
            raise

if __name__ == '__main__':
    asyncio.run(main())
